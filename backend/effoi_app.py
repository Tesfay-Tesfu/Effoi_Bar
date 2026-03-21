
"""
EFFOI RESTAURANT - Complete Clean Flask Application
Production-ready for Render.com with PostgreSQL
"""
import os
import json
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# ==================== PRODUCTION CONFIGURATION ====================
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Database configuration - Support both SQLite (local) and PostgreSQL (Render)
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///effoi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connection pool settings for PostgreSQL
if database_url and 'postgresql' in database_url:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,
        'max_overflow': 10
    }

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# Email configuration (optional - won't crash if not set)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', ('EFFOI Restaurant', 'noreply@effoirestaurant.com'))

# Base URL for absolute paths
app.config['BASE_URL'] = os.getenv('BASE_URL', 'https://www.effoirestaurant.com')

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# ==================== HELPER FUNCTIONS ====================
def get_upload_path(subfolder):
    """Get absolute upload path that works on both local and Render"""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(base_path, 'frontend', 'static', 'uploads', subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def get_available_times(date):
    """Get available reservation times for a given date"""
    all_times = []
    for hour in range(11, 22):  # 11 AM to 10 PM
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            all_times.append(time_str)
    
    # Get booked times from reservations
    booked_times = []
    reservations = Reservation.query.filter(
        Reservation.reservation_date == date,
        Reservation.status.in_(['pending', 'confirmed'])
    ).all()
    for res in reservations:
        booked_times.append(res.reservation_time)
    
    # Get blocked times from time blocks
    blocks = TimeBlock.query.filter(TimeBlock.block_date == date).all()
    for block in blocks:
        current = datetime.strptime(block.start_time, '%H:%M')
        end = datetime.strptime(block.end_time, '%H:%M')
        while current < end:
            time_str = current.strftime('%H:%M')
            booked_times.append(time_str)
            current += timedelta(minutes=30)
    
    # Return available times
    available = [t for t in all_times if t not in booked_times]
    return available

# ==================== TEMPLATE FILTERS ====================
@app.template_filter('from_json')
def from_json(value):
    """Convert JSON string to Python object"""
    if value:
        try:
            return json.loads(value)
        except:
            return []
    return []

@app.template_filter('format_currency')
def format_currency(value):
    """Format as USD currency"""
    return f"${value:.2f}"

# ==================== ADMIN DECORATOR ====================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Please login as admin to access this page.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== DATABASE MODELS ====================

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_super = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    menu_items = db.relationship('MenuItem', back_populates='category', lazy=True, cascade='all, delete-orphan')

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String(500))
    is_special = db.Column(db.Boolean, default=False)
    is_popular = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.relationship('Category', back_populates='menu_items')

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    author_email = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('BlogComment', back_populates='post', lazy=True, cascade='all, delete-orphan')

class BlogComment(db.Model):
    __tablename__ = 'blog_comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    author_email = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post = db.relationship('BlogPost', back_populates='comments')

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.String(10))
    location = db.Column(db.String(200))
    image_url = db.Column(db.String(500))
    price = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))
    reservation_date = db.Column(db.Date, nullable=False)
    reservation_time = db.Column(db.String(5), nullable=False)
    party_size = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TimeBlock(db.Model):
    __tablename__ = 'time_blocks'
    id = db.Column(db.Integer, primary_key=True)
    block_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    reason = db.Column(db.String(200))
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='text')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FAQ(db.Model):
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    meta_description = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HeroSlider(db.Model):
    __tablename__ = 'hero_sliders'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(500))
    image_url = db.Column(db.String(500), nullable=False)
    button_text = db.Column(db.String(100), default='View Menu')
    button_link = db.Column(db.String(500), default='/menu')
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CoffeeCeremony(db.Model):
    __tablename__ = 'coffee_ceremonies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventImage(db.Model):
    """Gallery images for events"""
    __tablename__ = 'event_images'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    event = db.relationship('Event', backref=db.backref('gallery_images', lazy=True, cascade='all, delete-orphan'))

class AboutUsImage(db.Model):
    """Gallery images for About Us page"""
    __tablename__ = 'about_us_images'
    
    id = db.Column(db.Integer, primary_key=True)
    about_us_id = db.Column(db.Integer, db.ForeignKey('about_us.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    about_us = db.relationship('AboutUs', backref=db.backref('gallery_images_rel', lazy=True, cascade='all, delete-orphan'))

# ==================== ABOUT US MODEL ====================
class AboutUs(db.Model):
    """About Us page content"""
    __tablename__ = 'about_us'
    
    id = db.Column(db.Integer, primary_key=True)
    hero_video_url = db.Column(db.String(500), default='https://player.vimeo.com/external/370468733.sd.mp4?s=90d2b19a3b4d1b3e4d1b3e4d1b3e4d1b3e4d1b3e4&profile_id=139')
    hero_title = db.Column(db.String(200), default='About EFFOI')
    
    card1_title = db.Column(db.String(200), default='Our Story')
    card1_text = db.Column(db.Text, default='Founded in 2024, EFFOI Restaurant brings the authentic taste of Ethiopia to Silver Spring.')
    card1_color = db.Column(db.String(50), default='danger')
    card1_icon = db.Column(db.String(50), default='utensils')
    
    card2_title = db.Column(db.String(200), default='Our Philosophy')
    card2_text = db.Column(db.Text, default='We believe in using only the freshest ingredients and traditional cooking methods.')
    card2_color = db.Column(db.String(50), default='warning')
    card2_icon = db.Column(db.String(50), default='leaf')
    
    card3_title = db.Column(db.String(200), default='Our Promise')
    card3_text = db.Column(db.Text, default='Every dish is prepared with love and care for an unforgettable experience.')
    card3_color = db.Column(db.String(50), default='success')
    card3_icon = db.Column(db.String(50), default='heart')
    
    stats_dishes = db.Column(db.Integer, default=100)
    stats_years = db.Column(db.Integer, default=15)
    stats_customers = db.Column(db.Integer, default=10000)
    stats_awards = db.Column(db.Integer, default=25)
    
    gallery_images = db.Column(db.Text, default='[]')
    meta_description = db.Column(db.String(300))
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== HEALTH CHECK ENDPOINT ====================
@app.route('/health')
def health_check():
    """Health check endpoint for Render monitoring"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ==================== CONTEXT PROCESSORS ====================
@app.context_processor
def inject_settings():
    settings = SiteSetting.query.all()
    settings_dict = {s.key: s.value for s in settings}
    return dict(settings=settings_dict)

@app.context_processor
def inject_now():
    return {'now': datetime.now}

@app.context_processor
def inject_recent_reviews():
    reviews = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).limit(5).all()
    return dict(recent_reviews=reviews)

@app.context_processor
def inject_hero_sliders():
    sliders = HeroSlider.query.filter_by(is_active=True).order_by(HeroSlider.display_order).all()
    return {'hero_sliders': sliders}

@app.context_processor
def inject_gallery_preview():
    images = GalleryImage.query.filter_by(is_active=True).order_by(GalleryImage.display_order).limit(4).all()
    return {'gallery_images': images}

@app.context_processor
def inject_about_us():
    about = AboutUs.query.first()
    return {'about_us': about}

# ==================== PUBLIC ROUTES ====================
@app.route('/')
def index():
    specials = MenuItem.query.filter_by(is_special=True, is_active=True).limit(6).all()
    events = Event.query.filter_by(is_active=True).order_by(Event.event_date).limit(3).all()
    return render_template('public/index.html', specials=specials, events=events)

@app.route('/menu')
def menu():
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order).all()
    return render_template('public/menu.html', categories=categories)

@app.route('/menu/<int:item_id>')
def menu_item_detail(item_id):
    item = MenuItem.query.get_or_404(item_id)
    return render_template('public/menu_item_detail.html', item=item)

@app.route('/events')
def events():
    upcoming = Event.query.filter_by(is_active=True).filter(Event.event_date >= datetime.now().date()).order_by(Event.event_date).all()
    past = Event.query.filter_by(is_active=True).filter(Event.event_date < datetime.now().date()).order_by(Event.event_date.desc()).limit(6).all()
    all_events = Event.query.filter_by(is_active=True).order_by(Event.event_date.desc()).all()
    return render_template('public/events.html', upcoming=upcoming, past=past, events=all_events)

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(status='approved').order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=9)
    return render_template('public/blog.html', posts=posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.status == 'approved':
        post.views += 1
        db.session.commit()
        comments = BlogComment.query.filter_by(post_id=post_id, status='approved').order_by(BlogComment.created_at.desc()).all()
        return render_template('public/blog_post.html', post=post, comments=comments)
    else:
        flash('This post is not available.', 'warning')
        return redirect(url_for('blog'))

@app.route('/blog/submit', methods=['GET', 'POST'])
def submit_blog():
    if request.method == 'POST':
        image_file = request.files.get('photo')
        image_url = request.form.get('image_url')
        
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            filename = f"{int(time.time())}_{filename}"
            
            upload_dir = get_upload_path('blog')
            file_path = os.path.join(upload_dir, filename)
            image_file.save(file_path)
            image_url = url_for('static', filename=f'uploads/blog/{filename}', _external=True)
        
        post = BlogPost(
            title=request.form.get('title'),
            content=request.form.get('content'),
            author_name=request.form.get('author_name'),
            author_email=request.form.get('author_email'),
            image_url=image_url,
            status='pending'
        )
        db.session.add(post)
        db.session.commit()
        
        flash('Thank you for sharing your experience! Your post will be reviewed shortly.', 'success')
        return redirect(url_for('blog'))
    
    return render_template('public/submit_blog.html')

@app.route('/blog/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.status == 'approved':
        comment = BlogComment(
            post_id=post_id,
            author_name=request.form.get('author_name'),
            author_email=request.form.get('author_email'),
            content=request.form.get('content'),
            status='pending'
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been submitted and will appear after approval.', 'success')
    return redirect(url_for('blog_post', post_id=post_id))

@app.route('/reviews')
def reviews():
    page = request.args.get('page', 1, type=int)
    reviews_list = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('public/reviews.html', reviews=reviews_list)

@app.route('/reviews/submit', methods=['POST'])
def submit_review():
    review = Review(
        customer_name=request.form.get('customer_name'),
        customer_email=request.form.get('customer_email'),
        rating=int(request.form.get('rating')),
        comment=request.form.get('comment'),
        is_approved=False
    )
    db.session.add(review)
    db.session.commit()
    
    flash('Thank you for your review! It will appear after approval.', 'success')
    return redirect(url_for('reviews'))

@app.route('/about')
def about():
    return render_template('public/about.html')

@app.route('/policy')
def policy():
    page = Page.query.filter_by(slug='policy').first()
    return render_template('public/page.html', page=page)

@app.route('/faq')
def faq():
    faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.display_order).all()
    return render_template('public/faq.html', faqs=faqs)

@app.route('/contact')
def contact():
    return render_template('public/contact.html')

@app.route('/contact/send', methods=['POST'])
def send_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    try:
        # Only try to send email if mail is configured
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            msg = Message(
                subject=f"Contact Form: {name}",
                recipients=[os.getenv('ADMIN_EMAIL', 'nigistme1277@gmail.com')],
                reply_to=email,
                body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            )
            mail.send(msg)
            flash('Your message has been sent. We\'ll get back to you soon!', 'success')
        else:
            # Log the message instead
            print(f"Contact message from {name} ({email}): {message}")
            flash('Your message has been received. We\'ll get back to you soon!', 'success')
    except Exception as e:
        print(f"Email error: {str(e)}")
        flash('Your message has been received. We\'ll get back to you soon!', 'success')
    
    return redirect(url_for('contact'))

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        try:
            reservation = Reservation(
                customer_name=request.form.get('name'),
                customer_email=request.form.get('email'),
                customer_phone=request.form.get('phone'),
                reservation_date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
                reservation_time=request.form.get('time'),
                party_size=int(request.form.get('party_size')),
                special_requests=request.form.get('special_requests'),
                status='pending'
            )
            db.session.add(reservation)
            db.session.commit()
            
            # Try to send email if configured
            if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
                try:
                    msg = Message(
                        subject="Reservation Request Received - EFFOI Restaurant",
                        recipients=[reservation.customer_email],
                        html=f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                            <div style="background-color: #8B1E1E; color: #FFD700; padding: 20px; text-align: center;">
                                <h1>EFFOI Restaurant</h1>
                            </div>
                            <div style="padding: 30px; background-color: #f9f9f9;">
                                <h2 style="color: #8B1E1E;">Thank You for Your Reservation Request</h2>
                                <p>Dear <strong>{reservation.customer_name}</strong>,</p>
                                <p>We have received your reservation request and will confirm it shortly.</p>
                                
                                <div style="background-color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                                    <h3 style="color: #8B1E1E; margin-top: 0;">Reservation Details:</h3>
                                    <p><strong>Date:</strong> {reservation.reservation_date.strftime('%B %d, %Y')}</p>
                                    <p><strong>Time:</strong> {reservation.reservation_time}</p>
                                    <p><strong>Party Size:</strong> {reservation.party_size} people</p>
                                </div>
                                
                                <p><strong>Status:</strong> <span style="color: #FFA500; font-weight: bold;">Pending Confirmation</span></p>
                                <p>We will send you another email once your reservation is confirmed.</p>
                                
                                <p>If you need to make any changes, please call us.</p>
                            </div>
                            <div style="background-color: #8B1E1E; color: white; padding: 15px; text-align: center; font-size: 12px;">
                                <p>8233 Fenton St, Silver Spring, MD 20910 | (240) 660-1337</p>
                            </div>
                        </div>
                        """
                    )
                    mail.send(msg)
                except Exception as e:
                    print(f"Email send error: {str(e)}")
            
            flash('Your reservation request has been submitted. We\'ll confirm shortly!', 'success')
            
        except Exception as e:
            print(f"Reservation error: {str(e)}")
            flash('There was an error processing your reservation. Please try again.', 'danger')
            db.session.rollback()
        
        return redirect(url_for('index'))
    
    return render_template('public/reserve.html')

@app.route('/get-available-times')
def get_available_times_route():
    date_str = request.args.get('date')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        times = get_available_times(date)
        return jsonify({'times': times})
    except:
        return jsonify({'times': []})

@app.route('/gallery')
def gallery():
    images = GalleryImage.query.filter_by(is_active=True).order_by(GalleryImage.display_order).all()
    return render_template('public/gallery.html', images=images)

# ==================== ADMIN ROUTES ====================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['is_admin'] = True
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    pending_posts = BlogPost.query.filter_by(status='pending').count()
    pending_comments = BlogComment.query.filter_by(status='pending').count()
    pending_reviews = Review.query.filter_by(is_approved=False).count()
    pending_reservations = Reservation.query.filter_by(status='pending').count()
    total_menu = MenuItem.query.count()
    total_events = Event.query.count()
    hero_sliders_count = HeroSlider.query.count()
    gallery_count = GalleryImage.query.count()
    
    recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(5).all()
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(5).all()
    recent_events = Event.query.order_by(Event.event_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         pending_posts=pending_posts,
                         pending_comments=pending_comments,
                         pending_reviews=pending_reviews,
                         pending_reservations=pending_reservations,
                         total_menu=total_menu,
                         total_events=total_events,
                         hero_sliders_count=hero_sliders_count,
                         gallery_count=gallery_count,
                         recent_reservations=recent_reservations,
                         recent_reviews=recent_reviews,
                         recent_events=recent_events)

@app.route('/admin/simple-dashboard')
@admin_required
def simple_dashboard():
    total_menu = MenuItem.query.count()
    categories = Category.query.count()
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - EFFOI</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        h1 {{ color: #8B1E1E; }}
        .stats {{ background: #eee; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .menu-links a {{ display: inline-block; margin: 5px; padding: 8px 15px; background: #8B1E1E; color: white; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>EFFOI Admin Dashboard</h1>
        <p>Welcome, {session.get('admin_username')}!</p>
        <div class="stats">
            <h3>Statistics</h3>
            <p>Total Menu Items: <strong>{total_menu}</strong></p>
            <p>Categories: <strong>{categories}</strong></p>
        </div>
        <div class="menu-links">
            <a href="/admin/menu">Manage Menu</a>
            <a href="/admin/categories">Manage Categories</a>
            <a href="/admin/reservations">View Reservations</a>
            <a href="/admin/logout">Logout</a>
        </div>
    </div>
</body>
</html>
"""
    return html

# ==================== ADMIN RESERVATIONS ====================
@app.route('/admin/reservations/update/<int:reservation_id>', methods=['POST'])
@admin_required
def admin_update_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'confirmed', 'cancelled']:
        old_status = reservation.status
        reservation.status = new_status
        db.session.commit()
        
        # Try to send email if configured and status changed
        if new_status != old_status and app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            try:
                status_colors = {'confirmed': '#28a745', 'cancelled': '#dc3545', 'pending': '#ffc107'}
                status_icons = {'confirmed': '✅', 'cancelled': '❌', 'pending': '⏳'}
                
                msg = Message(
                    subject=f"Reservation {new_status.title()} - EFFOI Restaurant",
                    recipients=[reservation.customer_email],
                    html=f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background-color: #8B1E1E; color: #FFD700; padding: 20px; text-align: center;">
                            <h1>EFFOI Restaurant</h1>
                        </div>
                        <div style="padding: 30px; background-color: #f9f9f9;">
                            <h2 style="color: #8B1E1E;">Reservation Status Update</h2>
                            <p>Dear <strong>{reservation.customer_name}</strong>,</p>
                            
                            <div style="background-color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                                <h3 style="color: #8B1E1E; margin-top: 0;">Your reservation has been:</h3>
                                <p style="font-size: 24px; color: {status_colors[new_status]};">
                                    {status_icons[new_status]} {new_status.title()}
                                </p>
                                
                                <h4 style="margin-top: 20px;">Reservation Details:</h4>
                                <p><strong>Date:</strong> {reservation.reservation_date.strftime('%B %d, %Y')}</p>
                                <p><strong>Time:</strong> {reservation.reservation_time}</p>
                                <p><strong>Party Size:</strong> {reservation.party_size} people</p>
                            </div>
                            
                            <p>If you have any questions, please call us.</p>
                        </div>
                        <div style="background-color: #8B1E1E; color: white; padding: 15px; text-align: center; font-size: 12px;">
                            <p>8233 Fenton St, Silver Spring, MD 20910 | (240) 660-1337</p>
                        </div>
                    </div>
                    """
                )
                mail.send(msg)
            except Exception as e:
                print(f"Email error: {str(e)}")
        
        flash(f'Reservation marked as {new_status}', 'success')
    
    return redirect(url_for('admin_reservations'))

@app.route('/admin/reservations')
@admin_required
def admin_reservations():
    status = request.args.get('status', 'all')
    query = Reservation.query
    if status != 'all':
        query = query.filter_by(status=status)
    reservations = query.order_by(Reservation.reservation_date.desc()).all()
    return render_template('admin/reservations.html', reservations=reservations, status=status)

@app.route('/admin/reservations/delete/<int:reservation_id>', methods=['POST'])
@admin_required
def admin_delete_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    db.session.delete(reservation)
    db.session.commit()
    flash('Reservation deleted successfully', 'success')
    return redirect(url_for('admin_reservations'))

# ==================== ADMIN CATEGORIES ====================
@app.route('/admin/categories')
@admin_required
def admin_categories():
    categories = Category.query.order_by(Category.display_order).all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@admin_required
def admin_add_category():
    if request.method == 'POST':
        category = Category(
            name=request.form.get('name'),
            display_order=int(request.form.get('display_order', 0)),
            is_active='is_active' in request.form
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully', 'success')
        return redirect(url_for('admin_categories'))
    return render_template('admin/category_form.html')

@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.display_order = int(request.form.get('display_order', 0))
        category.is_active = 'is_active' in request.form
        db.session.commit()
        flash('Category updated successfully', 'success')
        return redirect(url_for('admin_categories'))
    return render_template('admin/category_form.html', category=category)

@app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def admin_delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully', 'success')
    return redirect(url_for('admin_categories'))

# ==================== ADMIN MENU ====================
@app.route('/admin/menu')
@admin_required
def admin_menu():
    items = MenuItem.query.order_by(MenuItem.category_id, MenuItem.display_order).all()
    return render_template('admin/menu.html', items=items)

@app.route('/admin/menu/add', methods=['GET', 'POST'])
@admin_required
def admin_add_menu_item():
    if request.method == 'POST':
        image_file = request.files.get('image')
        image_url = request.form.get('image_url')
        
        if image_file and image_file.filename:
            filename = secure_filename(f"menu_{int(time.time())}_{image_file.filename}")
            upload_dir = get_upload_path('menu')
            file_path = os.path.join(upload_dir, filename)
            image_file.save(file_path)
            image_url = url_for('static', filename=f'uploads/menu/{filename}', _external=True)
        
        item = MenuItem(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=float(request.form.get('price')),
            category_id=int(request.form.get('category_id')),
            image_url=image_url,
            is_special='is_special' in request.form,
            is_popular='is_popular' in request.form,
            is_active='is_active' in request.form,
            display_order=int(request.form.get('display_order', 0))
        )
        db.session.add(item)
        db.session.commit()
        flash('Menu item added successfully', 'success')
        return redirect(url_for('admin_menu'))
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('admin/menu_form.html', categories=categories)

@app.route('/admin/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(f"menu_{int(time.time())}_{image_file.filename}")
            upload_dir = get_upload_path('menu')
            file_path = os.path.join(upload_dir, filename)
            image_file.save(file_path)
            item.image_url = url_for('static', filename=f'uploads/menu/{filename}', _external=True)
        elif request.form.get('image_url'):
            item.image_url = request.form.get('image_url')
        
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.price = float(request.form.get('price'))
        item.category_id = int(request.form.get('category_id'))
        item.is_special = 'is_special' in request.form
        item.is_popular = 'is_popular' in request.form
        item.is_active = 'is_active' in request.form
        item.display_order = int(request.form.get('display_order', 0))
        
        db.session.commit()
        flash('Menu item updated successfully', 'success')
        return redirect(url_for('admin_menu'))
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('admin/menu_form.html', item=item, categories=categories)

@app.route('/admin/menu/delete/<int:item_id>', methods=['POST'])
@admin_required
def admin_delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Menu item deleted successfully', 'success')
    return redirect(url_for('admin_menu'))

# ==================== ADMIN EVENTS ====================
@app.route('/admin/events')
@admin_required
def admin_events():
    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('admin/events.html', events=events)

@app.route('/admin/events/add', methods=['GET', 'POST'])
@admin_required
def admin_add_event():
    if request.method == 'POST':
        image_file = request.files.get('image')
        image_url = request.form.get('image_url')
        
        if image_file and image_file.filename:
            filename = secure_filename(f"event_{int(time.time())}_{image_file.filename}")
            upload_dir = get_upload_path('events')
            file_path = os.path.join(upload_dir, filename)
            image_file.save(file_path)
            image_url = url_for('static', filename=f'uploads/events/{filename}', _external=True)
        
        event = Event(
            title=request.form.get('title'),
            description=request.form.get('description'),
            event_date=datetime.strptime(request.form.get('event_date'), '%Y-%m-%d').date(),
            event_time=request.form.get('event_time'),
            location=request.form.get('location'),
            image_url=image_url,
            price=float(request.form.get('price', 0)),
            is_active='is_active' in request.form
        )
        db.session.add(event)
        db.session.commit()
        flash('Event added successfully', 'success')
        return redirect(url_for('admin_events'))
    return render_template('admin/event_form.html')

@app.route('/admin/events/edit/<int:event_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(f"event_{int(time.time())}_{image_file.filename}")
            upload_dir = get_upload_path('events')
            file_path = os.path.join(upload_dir, filename)
            image_file.save(file_path)
            event.image_url = url_for('static', filename=f'uploads/events/{filename}', _external=True)
        elif request.form.get('image_url'):
            event.image_url = request.form.get('image_url')
        
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.event_date = datetime.strptime(request.form.get('event_date'), '%Y-%m-%d').date()
        event.event_time = request.form.get('event_time')
        event.location = request.form.get('location')
        event.price = float(request.form.get('price', 0))
        event.is_active = 'is_active' in request.form
        
        db.session.commit()
        flash('Event updated successfully', 'success')
        return redirect(url_for('admin_events'))
    
    return render_template('admin/event_form.html', event=event)

@app.route('/admin/events/delete/<int:event_id>', methods=['POST'])
@admin_required
def admin_delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully', 'success')
    return redirect(url_for('admin_events'))

@app.route('/admin/events/toggle/<int:event_id>', methods=['POST'])
@admin_required
def admin_toggle_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.is_active = not event.is_active
    db.session.commit()
    flash(f'Event {"activated" if event.is_active else "deactivated"} successfully', 'success')
    return redirect(url_for('admin_events'))

# ==================== ADMIN BLOG ====================
@app.route('/admin/blog')
@admin_required
def admin_blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/blog.html', posts=posts)

@app.route('/admin/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def admin_blog_edit(post_id):
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author_name = request.form.get('author_name')
        author_email = request.form.get('author_email')
        status = request.form.get('status')
        
        post.title = title
        post.content = content
        post.author_name = author_name
        post.author_email = author_email if author_email else None
        post.status = status if status else post.status
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(f"blog_{int(time.time())}_{image_file.filename}")
            upload_dir = get_upload_path('blog')
            file_path = os.path.join(upload_dir, filename)
            image_file.save(file_path)
            post.image_url = url_for('static', filename=f'uploads/blog/{filename}', _external=True)
        elif request.form.get('image_url'):
            post.image_url = request.form.get('image_url')
        
        db.session.commit()
        flash('Blog post updated successfully', 'success')
        return redirect(url_for('admin_blog'))
    
    return render_template('admin/blog_form.html', post=post)

@app.route('/admin/blog/delete/<int:post_id>', methods=['POST'])
@admin_required
def admin_blog_delete(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully', 'success')
    return redirect(url_for('admin_blog'))

# ==================== ADMIN COMMENTS ====================
@app.route('/admin/comments')
@admin_required
def admin_comments():
    comments = BlogComment.query.order_by(BlogComment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=comments)

@app.route('/admin/comments/approve/<int:comment_id>', methods=['POST'])
@admin_required
def admin_approve_comment(comment_id):
    comment = BlogComment.query.get_or_404(comment_id)
    comment.status = 'approved'
    db.session.commit()
    flash('Comment approved', 'success')
    return redirect(url_for('admin_comments'))

@app.route('/admin/comments/reject/<int:comment_id>', methods=['POST'])
@admin_required
def admin_reject_comment(comment_id):
    comment = BlogComment.query.get_or_404(comment_id)
    comment.status = 'rejected'
    db.session.commit()
    flash('Comment rejected', 'success')
    return redirect(url_for('admin_comments'))

@app.route('/admin/comments/delete/<int:comment_id>', methods=['POST'])
@admin_required
def admin_delete_comment(comment_id):
    comment = BlogComment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted', 'success')
    return redirect(url_for('admin_comments'))

# ==================== ADMIN REVIEWS ====================
@app.route('/admin/reviews')
@admin_required
def admin_reviews():
    reviews_list = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews_list)

@app.route('/admin/reviews/approve/<int:review_id>', methods=['POST'])
@admin_required
def admin_approve_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = True
    db.session.commit()
    flash('Review approved successfully', 'success')
    return redirect(url_for('admin_reviews'))

@app.route('/admin/reviews/delete/<int:review_id>', methods=['POST'])
@admin_required
def admin_delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted successfully', 'success')
    return redirect(url_for('admin_reviews'))

# ==================== ADMIN TIME BLOCKS ====================
@app.route('/admin/time-blocks')
@admin_required
def admin_time_blocks():
    blocks = TimeBlock.query.order_by(TimeBlock.block_date.desc()).all()
    return render_template('admin/time_blocks.html', blocks=blocks)

@app.route('/admin/time-blocks/add', methods=['POST'])
@admin_required
def admin_add_time_block():
    block = TimeBlock(
        block_date=datetime.strptime(request.form.get('block_date'), '%Y-%m-%d').date(),
        start_time=request.form.get('start_time'),
        end_time=request.form.get('end_time'),
        reason=request.form.get('reason'),
        created_by=session.get('admin_username', 'admin')
    )
    db.session.add(block)
    db.session.commit()
    flash('Time block added successfully', 'success')
    return redirect(url_for('admin_time_blocks'))

@app.route('/admin/time-blocks/delete/<int:block_id>', methods=['POST'])
@admin_required
def admin_delete_time_block(block_id):
    block = TimeBlock.query.get_or_404(block_id)
    db.session.delete(block)
    db.session.commit()
    flash('Time block deleted successfully', 'success')
    return redirect(url_for('admin_time_blocks'))

# ==================== ADMIN FAQ ====================
@app.route('/admin/faqs')
@admin_required
def admin_faqs():
    faqs = FAQ.query.order_by(FAQ.display_order).all()
    return render_template('admin/faqs.html', faqs=faqs)

@app.route('/admin/faqs/add', methods=['GET', 'POST'])
@admin_required
def admin_add_faq():
    if request.method == 'POST':
        faq = FAQ(
            question=request.form.get('question'),
            answer=request.form.get('answer'),
            display_order=int(request.form.get('display_order', 0)),
            is_active='is_active' in request.form
        )
        db.session.add(faq)
        db.session.commit()
        flash('FAQ added successfully', 'success')
        return redirect(url_for('admin_faqs'))
    return render_template('admin/faq_form.html')

@app.route('/admin/faqs/edit/<int:faq_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    if request.method == 'POST':
        faq.question = request.form.get('question')
        faq.answer = request.form.get('answer')
        faq.display_order = int(request.form.get('display_order', 0))
        faq.is_active = 'is_active' in request.form
        db.session.commit()
        flash('FAQ updated successfully', 'success')
        return redirect(url_for('admin_faqs'))
    return render_template('admin/faq_form.html', faq=faq)

@app.route('/admin/faqs/delete/<int:faq_id>', methods=['POST'])
@admin_required
def admin_delete_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ deleted successfully', 'success')
    return redirect(url_for('admin_faqs'))

# ==================== ADMIN PAGES ====================
@app.route('/admin/pages')
@admin_required
def admin_pages():
    pages = Page.query.all()
    return render_template('admin/pages.html', pages=pages)

@app.route('/admin/pages/edit/<string:slug>', methods=['GET', 'POST'])
@admin_required
def admin_edit_page(slug):
    page = Page.query.filter_by(slug=slug).first()
    if not page:
        page = Page(slug=slug, title=slug.replace('-', ' ').title(), content='')
        db.session.add(page)
        db.session.commit()
    
    if request.method == 'POST':
        page.title = request.form.get('title')
        page.content = request.form.get('content')
        page.meta_description = request.form.get('meta_description')
        page.is_active = 'is_active' in request.form
        db.session.commit()
        flash('Page updated successfully', 'success')
        return redirect(url_for('admin_pages'))
    
    return render_template('admin/page_form.html', page=page)

# ==================== ADMIN HERO SLIDERS ====================
@app.route('/admin/hero-sliders')
@admin_required
def admin_hero_sliders():
    sliders = HeroSlider.query.order_by(HeroSlider.display_order).all()
    return render_template('admin/hero_sliders.html', sliders=sliders)

@app.route('/admin/hero-sliders/add', methods=['GET', 'POST'])
@admin_required
def admin_add_slider():
    if request.method == 'POST':
        image_file = request.files.get('image')
        image_url = request.form.get('image_url')
        
        if image_file and image_file.filename:
            filename = secure_filename(f"slider_{int(time.time())}_{image_file.filename}")
            upload_dir = get_upload_path('sliders')
            file_path = os.path.join(upload_dir, filename)
            image_file.save(file_path)
            image_url = url_for('static', filename=f'uploads/sliders/{filename}', _external=True)
        
        slider = HeroSlider(
            title=request.form.get('title'),
            subtitle=request.form.get('subtitle'),
            image_url=image_url,
            button_text=request.form.get('button_text', 'View Menu'),
            button_link=request.form.get('button_link', '/menu'),
            display_order=int(request.form.get('display_order', 0)),
            is_active='is_active' in request.form
        )
        db.session.add(slider)
        db.session.commit()
        flash('Hero slider added successfully', 'success')
        return redirect(url_for('admin_hero_sliders'))
    
    return render_template('admin/hero_slider_form.html')

@app.route('/admin/hero-sliders/edit/<int:slider_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_slider(slider_id):
    slider = HeroSlider.query.get_or_404(slider_id)
    
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(f"slider_{int(time.time())}_{image_file.filename}")
            upload_dir = get_upload_path('sliders')
            file_path = os.path.join(upload_dir, filename)
            image_file.save(file_path)
            slider.image_url = url_for('static', filename=f'uploads/sliders/{filename}', _external=True)
        elif request.form.get('image_url'):
            slider.image_url = request.form.get('image_url')
        
        slider.title = request.form.get('title')
        slider.subtitle = request.form.get('subtitle')
        slider.button_text = request.form.get('button_text', 'View Menu')
        slider.button_link = request.form.get('button_link', '/menu')
        slider.display_order = int(request.form.get('display_order', 0))
        slider.is_active = 'is_active' in request.form
        
        db.session.commit()
        flash('Hero slider updated successfully', 'success')
        return redirect(url_for('admin_hero_sliders'))
    
    return render_template('admin/hero_slider_form.html', slider=slider)

@app.route('/admin/hero-sliders/toggle/<int:slider_id>', methods=['POST'])
@admin_required
def admin_toggle_slider(slider_id):
    slider = HeroSlider.query.get_or_404(slider_id)
    slider.is_active = not slider.is_active
    db.session.commit()
    flash(f'Slider {"activated" if slider.is_active else "deactivated"} successfully', 'success')
    return redirect(url_for('admin_hero_sliders'))

@app.route('/admin/hero-sliders/delete/<int:slider_id>', methods=['POST'])
@admin_required
def admin_delete_slider(slider_id):
    slider = HeroSlider.query.get_or_404(slider_id)
    db.session.delete(slider)
    db.session.commit()
    flash('Hero slider deleted successfully', 'success')
    return redirect(url_for('admin_hero_sliders'))

# ==================== ADMIN GALLERY ====================
@app.route('/admin/gallery')
@admin_required
def admin_gallery():
    images = GalleryImage.query.order_by(GalleryImage.display_order).all()
    return render_template('admin/gallery.html', images=images)

@app.route('/admin/gallery/upload', methods=['POST'])
@admin_required
def admin_upload_gallery():
    image_file = request.files.get('image')
    if image_file and image_file.filename:
        filename = secure_filename(f"gallery_{int(time.time())}_{image_file.filename}")
        upload_dir = get_upload_path('gallery')
        file_path = os.path.join(upload_dir, filename)
        image_file.save(file_path)
        
        image = GalleryImage(
            title=request.form.get('title'),
            image_url=url_for('static', filename=f'uploads/gallery/{filename}', _external=True),
            category=request.form.get('category'),
            display_order=int(request.form.get('display_order', 0)),
            is_active=True
        )
        db.session.add(image)
        db.session.commit()
        flash('Image uploaded successfully', 'success')
    else:
        flash('No image file provided', 'danger')
    
    return redirect(url_for('admin_gallery'))

@app.route('/admin/gallery/edit/<int:image_id>', methods=['POST'])
@admin_required
def admin_edit_gallery(image_id):
    image = GalleryImage.query.get_or_404(image_id)
    
    image.title = request.form.get('title')
    image.category = request.form.get('category')
    image.display_order = int(request.form.get('display_order', 0))
    image.is_active = 'is_active' in request.form
    
    image_file = request.files.get('image')
    if image_file and image_file.filename:
        filename = secure_filename(f"gallery_{int(time.time())}_{image_file.filename}")
        upload_dir = get_upload_path('gallery')
        file_path = os.path.join(upload_dir, filename)
        image_file.save(file_path)
        image.image_url = url_for('static', filename=f'uploads/gallery/{filename}', _external=True)
    
    db.session.commit()
    flash('Image updated successfully', 'success')
    return redirect(url_for('admin_gallery'))

@app.route('/admin/gallery/delete/<int:image_id>', methods=['POST'])
@admin_required
def admin_delete_gallery(image_id):
    image = GalleryImage.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully', 'success')
    return redirect(url_for('admin_gallery'))

# ==================== ADMIN SPECIALS ====================
@app.route('/admin/menu/toggle-special/<int:item_id>', methods=['POST'])
@admin_required
def admin_toggle_special(item_id):
    item = MenuItem.query.get_or_404(item_id)
    item.is_special = not item.is_special
    db.session.commit()
    flash(f'"{item.name}" {"added to" if item.is_special else "removed from"} specials', 'success')
    return redirect(url_for('admin_specials'))

@app.route('/admin/menu/toggle-popular/<int:item_id>', methods=['POST'])
@admin_required
def admin_toggle_popular(item_id):
    item = MenuItem.query.get_or_404(item_id)
    item.is_popular = not item.is_popular
    db.session.commit()
    flash(f'"{item.name}" {"marked as" if item.is_popular else "unmarked as"} popular', 'success')
    return redirect(url_for('admin_specials'))

@app.route('/admin/specials')
@admin_required
def admin_specials():
    items = MenuItem.query.order_by(MenuItem.category_id, MenuItem.name).all()
    return render_template('admin/specials.html', items=items)

# ==================== ADMIN ABOUT PAGE ====================
@app.route('/admin/about/edit', methods=['GET', 'POST'])
@admin_required
def admin_about_edit():
    about = AboutUs.query.first()
    if not about:
        about = AboutUs()
        db.session.add(about)
        db.session.commit()
    
    if request.method == 'POST':
        # Hero Section
        about.hero_title = request.form.get('hero_title', 'About EFFOI')
        
        video_file = request.files.get('hero_video')
        if video_file and video_file.filename:
            filename = secure_filename(video_file.filename)
            filename = f"about_video_{int(time.time())}_{filename}"
            upload_dir = get_upload_path('about')
            file_path = os.path.join(upload_dir, filename)
            video_file.save(file_path)
            about.hero_video_url = url_for('static', filename=f'uploads/about/{filename}', _external=True)
        elif request.form.get('hero_video_url'):
            about.hero_video_url = request.form.get('hero_video_url')
        
        # Cards
        about.card1_title = request.form.get('card1_title', 'Our Story')
        about.card1_text = request.form.get('card1_text', '')
        about.card1_color = request.form.get('card1_color', 'danger')
        about.card1_icon = request.form.get('card1_icon', 'utensils')
        
        about.card2_title = request.form.get('card2_title', 'Our Philosophy')
        about.card2_text = request.form.get('card2_text', '')
        about.card2_color = request.form.get('card2_color', 'warning')
        about.card2_icon = request.form.get('card2_icon', 'leaf')
        
        about.card3_title = request.form.get('card3_title', 'Our Promise')
        about.card3_text = request.form.get('card3_text', '')
        about.card3_color = request.form.get('card3_color', 'success')
        about.card3_icon = request.form.get('card3_icon', 'heart')
        
        # Stats
        try:
            about.stats_dishes = int(request.form.get('stats_dishes', 100))
            about.stats_years = int(request.form.get('stats_years', 15))
            about.stats_customers = int(request.form.get('stats_customers', 10000))
            about.stats_awards = int(request.form.get('stats_awards', 25))
        except:
            pass
        
        # SEO
        about.meta_description = request.form.get('meta_description')
        
        try:
            db.session.commit()
            flash('About Us page updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving: {str(e)}', 'danger')
        
        return redirect(url_for('admin_about_edit'))
    
    gallery_images = AboutUsImage.query.filter_by(about_us_id=about.id, is_active=True).order_by(AboutUsImage.display_order).all()
    return render_template('admin/about_edit.html', about=about, gallery_images=gallery_images)

# ==================== ABOUT US GALLERY ====================
@app.route('/admin/about/gallery/upload', methods=['POST'])
@admin_required
def admin_about_gallery_upload():
    about = AboutUs.query.first()
    if not about:
        about = AboutUs()
        db.session.add(about)
        db.session.commit()
    
    files = request.files.getlist('images')
    uploaded_count = 0
    
    for i, file in enumerate(files):
        if file and file.filename:
            title = request.form.get(f'title_{i}', '')
            filename = secure_filename(file.filename)
            filename = f"about_gallery_{int(time.time())}_{i}_{filename}"
            upload_dir = get_upload_path('about/gallery')
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            image = AboutUsImage(
                about_us_id=about.id,
                image_url=url_for('static', filename=f'uploads/about/gallery/{filename}', _external=True),
                title=title,
                display_order=uploaded_count,
                is_active=True
            )
            db.session.add(image)
            uploaded_count += 1
    
    db.session.commit()
    return jsonify({'success': True, 'uploaded': uploaded_count})

@app.route('/admin/about/gallery/update/<int:image_id>', methods=['POST'])
@admin_required
def admin_about_gallery_update(image_id):
    image = AboutUsImage.query.get_or_404(image_id)
    data = request.get_json()
    
    if data and 'title' in data:
        image.title = data['title']
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 400

@app.route('/admin/about/gallery/delete/<int:image_id>', methods=['POST'])
@admin_required
def admin_about_gallery_delete(image_id):
    image = AboutUsImage.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    return jsonify({'success': True})

# ==================== ADMIN EVENT GALLERY ====================
@app.route('/admin/event-gallery/<int:event_id>')
@admin_required
def admin_event_gallery(event_id):
    event = Event.query.get_or_404(event_id)
    images = EventImage.query.filter_by(event_id=event_id).order_by(EventImage.display_order).all()
    return render_template('admin/event_gallery.html', event=event, images=images)

@app.route('/admin/event-gallery/upload/<int:event_id>', methods=['POST'])
@admin_required
def admin_upload_event_gallery(event_id):
    event = Event.query.get_or_404(event_id)
    
    files = request.files.getlist('images')
    default_title = request.form.get('default_title', '')
    uploaded_count = 0
    
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            filename = f"event_{event_id}_{int(time.time())}_{uploaded_count}_{filename}"
            upload_dir = get_upload_path('events/gallery')
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            image = EventImage(
                event_id=event_id,
                image_url=url_for('static', filename=f'uploads/events/gallery/{filename}', _external=True),
                title=default_title or f"{event.title} - Image {uploaded_count + 1}",
                display_order=uploaded_count,
                is_active=True
            )
            db.session.add(image)
            uploaded_count += 1
    
    db.session.commit()
    flash(f'Successfully uploaded {uploaded_count} images!', 'success')
    return redirect(url_for('admin_event_gallery', event_id=event_id))

@app.route('/admin/event-gallery/edit/<int:image_id>', methods=['POST'])
@admin_required
def admin_edit_event_gallery(image_id):
    image = EventImage.query.get_or_404(image_id)
    
    image.title = request.form.get('title', image.title)
    image.display_order = int(request.form.get('display_order', image.display_order))
    image.is_active = 'is_active' in request.form
    
    new_image = request.files.get('image')
    if new_image and new_image.filename:
        filename = secure_filename(new_image.filename)
        filename = f"event_{image.event_id}_{int(time.time())}_{filename}"
        upload_dir = get_upload_path('events/gallery')
        file_path = os.path.join(upload_dir, filename)
        new_image.save(file_path)
        image.image_url = url_for('static', filename=f'uploads/events/gallery/{filename}', _external=True)
    
    db.session.commit()
    flash('Image updated successfully!', 'success')
    return redirect(url_for('admin_event_gallery', event_id=image.event_id))

@app.route('/admin/event-gallery/delete/<int:image_id>', methods=['POST'])
@admin_required
def admin_delete_event_gallery(image_id):
    image = EventImage.query.get_or_404(image_id)
    event_id = image.event_id
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('admin_event_gallery', event_id=event_id))

# ==================== ADMIN SETTINGS ====================
@app.route('/admin/settings')
@admin_required
def admin_settings():
    settings = SiteSetting.query.all()
    settings_dict = {s.key: s for s in settings}
    return render_template('admin/settings.html', settings=settings_dict)

@app.route('/admin/settings/update', methods=['POST'])
@admin_required
def admin_update_settings():
    restaurant_settings = {
        'restaurant_name': request.form.get('restaurant_name', 'EFFOI RESTAURANT'),
        'logo_url': request.form.get('logo_url', 'https://raw.githubusercontent.com/Tesfay-Tesfu/Mella-Technollogy-LLC-Python-Course/main/Effoi_logo3.png'),
        'logo_text': request.form.get('logo_text', 'EFFOI RESTAURANT'),
        'address': request.form.get('address', '8233 Fenton St, Silver Spring, MD 20910'),
        'phone': request.form.get('phone', '+1 (240) 660-1337'),
        'email': request.form.get('email', 'nigistme1277@gmail.com'),
        'map_icon_color': request.form.get('map_icon_color', '#4285F4'),
        'hours': request.form.get('hours', 'Mon-Sun: 11:00 AM - 10:00 PM'),
        'hours_detailed': request.form.get('hours_detailed', 'Monday-Friday:11am-10pm,Saturday:11am-11pm,Sunday:11am-9pm'),
    }
    
    header_settings = {
        'header_bg_color': request.form.get('header_bg_color', '#8B1E1E'),
        'header_text_color': request.form.get('header_text_color', '#ffffff'),
    }
    
    footer_settings = {
        'footer_text': request.form.get('footer_text', 'Experience the taste of Ethiopia at EFFOI'),
        'copyright_text': request.form.get('copyright_text', '© 2026 EFFOI RESTAURANT. All rights reserved.'),
        'footer_bg_color': request.form.get('footer_bg_color', '#1a2c3e'),
        'footer_text_color': request.form.get('footer_text_color', '#ffffff'),
    }
    
    social_settings = {
        'facebook_url': request.form.get('facebook_url', '#'),
        'instagram_url': request.form.get('instagram_url', '#'),
        'twitter_url': request.form.get('twitter_url', '#'),
        'yelp_url': request.form.get('yelp_url', '#'),
    }
    
    all_settings = {**restaurant_settings, **header_settings, **footer_settings, **social_settings}
    
    for key, value in all_settings.items():
        setting = SiteSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = SiteSetting(key=key, value=value)
            db.session.add(setting)
    
    db.session.commit()
    flash('Settings updated successfully', 'success')
    return redirect(url_for('admin_settings'))

# ==================== API ENDPOINTS ====================
@app.route('/api/blocked-times')
def get_blocked_times():
    """Get all upcoming blocked time slots"""
    try:
        today = datetime.now().date()
        blocks = TimeBlock.query.filter(TimeBlock.block_date >= today).order_by(TimeBlock.block_date, TimeBlock.start_time).limit(10).all()
        
        result = []
        for block in blocks:
            result.append({
                'date': block.block_date.strftime('%b %d, %Y'),
                'start_time': block.start_time,
                'end_time': block.end_time,
                'reason': block.reason if block.reason else 'Private Event'
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify([])

@app.route('/api/gallery-image/<int:image_id>')
def get_gallery_image(image_id):
    """Get gallery image details for editing"""
    image = GalleryImage.query.get_or_404(image_id)
    return jsonify({
        'id': image.id,
        'title': image.title,
        'category': image.category,
        'image_url': image.image_url,
        'display_order': image.display_order,
        'is_active': image.is_active
    })

# ==================== INITIALIZE DATABASE ====================
def init_db():
    """Initialize database and create default admin"""
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not Admin.query.first():
            admin = Admin(
                username='admin',
                email='admin@effoirestaurant.com',
                is_super=True
            )
            admin_password = os.getenv('ADMIN_PASSWORD', 'EffoiAdmin2024!')
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Default admin created with password: {admin_password}")
        
        # Create default settings if not exists
        default_settings = {
            'restaurant_name': 'EFFOI RESTAURANT',
            'address': '8233 Fenton St, Silver Spring, MD 20910',
            'phone': '+1 (240) 660-1337',
            'email': 'nigistme1277@gmail.com',
            'hours': 'Mon-Sun: 11:00 AM - 10:00 PM'
        }
        
        for key, value in default_settings.items():
            if not SiteSetting.query.filter_by(key=key).first():
                setting = SiteSetting(key=key, value=value)
                db.session.add(setting)
        
        db.session.commit()
        print("✅ Database initialized")

# ==================== RUN APPLICATION ====================
if __name__ == '__main__':
    # Create all upload directories
    upload_folders = ['blog', 'sliders', 'events', 'events/gallery', 'gallery', 'menu', 'about', 'about/gallery', 'temp']
    for folder in upload_folders:
        get_upload_path(folder)
        print(f"✅ Created upload folder: {folder}")
    
    # Initialize database
    init_db()
    
    # Get port from environment (Render sets PORT)
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
