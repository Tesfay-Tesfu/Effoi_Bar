"""
EFFOI RESTAURANT - Complete Clean Flask Application
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
from urllib.parse import urlparse
from dotenv import load_dotenv
import secrets
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from email_validator import validate_email, EmailNotValidError

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise RuntimeError('DATABASE_URL environment variable must be set for PostgreSQL.')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 100MB

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'tesfaymn402@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD','hkdc ohxr ptoo xmhz')
app.config['MAIL_DEFAULT_SENDER'] = ('EFFOI Restaurant', 'nigistme1277@gmail.com')

# Base URL
app.config['BASE_URL'] = os.getenv('BASE_URL', 'http://localhost:5001')

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Limiter for rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["10 per day"]
)

# blocked main domain
BLOCKED_DOMAINS = {
    "mailinator.com",
    "10minutemail.com",
    "guerrillamail.com",
    "tempmail.com",
    "yopmail.com",
    "trashmail.com"
}

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
    reservation_time = db.Column(db.String(10), nullable=False)
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

# Add this model to effoi_app.py
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
    
    # Relationship
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
    
    # Relationship
    about_us = db.relationship('AboutUs', backref=db.backref('gallery_images_rel', lazy=True, cascade='all, delete-orphan'))

# ==================== ABOUT US MODEL ====================
class AboutUs(db.Model):
    """About Us page content"""
    __tablename__ = 'about_us'
    
    id = db.Column(db.Integer, primary_key=True)
    # Hero Section
    hero_video_url = db.Column(db.String(500), default='https://player.vimeo.com/external/370468733.sd.mp4?s=90d2b19a3b4d1b3e4d1b3e4d1b3e4d1b3e4d1b3e4&profile_id=139')
    hero_title = db.Column(db.String(200), default='About EFFOI')
    
    # Card 1 - Our Story
    card1_title = db.Column(db.String(200), default='Our Story')
    card1_text = db.Column(db.Text, default='Founded in 2010, EFFOI Restaurant brings the authentic taste of Ethiopia to Silver Spring. Our recipes have been passed down through generations, preserving the rich culinary heritage of Ethiopia.')
    card1_color = db.Column(db.String(50), default='danger')  # bg-danger, bg-warning, bg-success
    card1_icon = db.Column(db.String(50), default='utensils')  # Font Awesome icon
    
    # Card 2 - Our Philosophy
    card2_title = db.Column(db.String(200), default='Our Philosophy')
    card2_text = db.Column(db.Text, default='We believe in using only the freshest ingredients, traditional cooking methods, and serving with the warm hospitality that Ethiopia is known for.')
    card2_color = db.Column(db.String(50), default='warning')
    card2_icon = db.Column(db.String(50), default='leaf')
    
    # Card 3 - Our Promise
    card3_title = db.Column(db.String(200), default='Our Promise')
    card3_text = db.Column(db.Text, default='Every dish is prepared with love and care, ensuring an unforgettable dining experience that will keep you coming back for more.')
    card3_color = db.Column(db.String(50), default='success')
    card3_icon = db.Column(db.String(50), default='heart')
    
    # Stats Section
    stats_dishes = db.Column(db.Integer, default=100)
    stats_years = db.Column(db.Integer, default=15)
    stats_customers = db.Column(db.Integer, default=10000)
    stats_awards = db.Column(db.Integer, default=25)
    
    # Gallery Images (comma-separated URLs or JSON)
    gallery_images = db.Column(db.Text, default='[]')  # Store as JSON array
    
    # SEO
    meta_description = db.Column(db.String(300))
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== HELPER FUNCTIONS ====================
def get_available_times(date):
    all_times = []
    for hour in range(11, 22):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            all_times.append(time_str)
    
    booked_times = []
    reservations = Reservation.query.filter(
        Reservation.reservation_date == date,
        Reservation.status.in_(['pending', 'confirmed'])
    ).all()
    for res in reservations:
        booked_times.append(res.reservation_time)
    
    blocks = TimeBlock.query.filter(TimeBlock.block_date == date).all()
    for block in blocks:
        current = datetime.strptime(block.start_time, '%H:%M')
        end = datetime.strptime(block.end_time, '%H:%M')
        while current < end:
            time_str = current.strftime('%H:%M')
            booked_times.append(time_str)
            current += timedelta(minutes=30)
    
    available = [t for t in all_times if t not in booked_times]
    return available

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
    all_events = Event.query.filter_by(is_active=True).order_by(Event.event_date.desc()).all()  # Add this line
    return render_template('public/events.html', upcoming=upcoming, past=past, events=all_events)  # Add events=all_events

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

        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            author_name = request.form.get('author_name', '').strip()
            author_email = request.form.get('author_email', '').strip().lower()

            # -------------------------
            # Validate required fields
            # -------------------------
            if not title or not content or not author_name or not author_email:
                flash(
                    'Please fill in all required fields.',
                    'danger'
                )
                return render_template('public/submit_blog.html')

            # -------------------------
            # Prevent duplicate titles
            # -------------------------
            duplicate_title = BlogPost.query.filter(
                BlogPost.author_email == author_email,
                BlogPost.title == title
            ).first()

            if duplicate_title:
                flash(
                    'You have already submitted a blog post with this title.',
                    'warning'
                )
                return render_template('public/submit_blog.html')

            # -------------------------
            # Prevent multiple pending posts
            # -------------------------
            pending_post = BlogPost.query.filter(
                BlogPost.author_email == author_email,
                BlogPost.status == 'pending'
            ).first()

            if pending_post:
                flash(
                    'You already have a blog post awaiting review.',
                    'warning'
                )
                return render_template('public/submit_blog.html')

            # -------------------------
            # Cooldown (1 hour)
            # -------------------------
            recent_post = BlogPost.query.filter(
                BlogPost.author_email == author_email,
                BlogPost.created_at >= (
                    datetime.utcnow() - timedelta(hours=1)
                )
            ).first()

            if recent_post:
                flash(
                    'Please wait one hour before submitting another blog post.',
                    'warning'
                )
                return render_template('public/submit_blog.html')

            # -------------------------
            # Handle Image Upload
            # -------------------------
            image_file = request.files.get('photo')
            image_url = request.form.get('image_url')

            if image_file and image_file.filename:

                filename = secure_filename(
                    image_file.filename
                )

                filename = (
                    f"{int(time.time())}_{filename}"
                )

                upload_dir = os.path.join(
                    app.root_path,
                    'frontend',
                    'static',
                    'uploads',
                    'blog'
                )

                os.makedirs(
                    upload_dir,
                    exist_ok=True
                )

                file_path = os.path.join(
                    upload_dir,
                    filename
                )

                try:
                    image_file.save(file_path)

                    if not os.path.exists(file_path):
                        flash(
                            'Uploaded image could not be saved.',
                            'danger'
                        )
                        return render_template(
                            'public/submit_blog.html'
                        )

                    image_url = url_for(
                        'static',
                        filename=f'uploads/blog/{filename}',
                        _external=True
                    )

                except Exception as e:

                    app.logger.error(
                        f"Blog image upload error: {e}"
                    )

                    flash(
                        'Failed to save uploaded image.',
                        'danger'
                    )

                    return render_template(
                        'public/submit_blog.html'
                    )

            # -------------------------
            # Save Blog Post
            # -------------------------
            post = BlogPost(
                title=title,
                content=content,
                author_name=author_name,
                author_email=author_email,
                image_url=image_url,
                status='pending'
            )

            db.session.add(post)
            db.session.commit()

            flash(
                'Thank you for sharing your experience! Your post will be reviewed shortly.',
                'success'
            )

            return redirect(
                url_for('blog')
            )

        except Exception as e:

            db.session.rollback()

            app.logger.error(
                f"Blog submission error: {e}"
            )

            flash(
                'An error occurred while submitting your blog post.',
                'danger'
            )

            return render_template(
                'public/submit_blog.html'
            )

    return render_template(
        'public/submit_blog.html'
    )

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
    reviews = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('public/reviews.html', reviews=reviews)

@app.route('/reviews/submit', methods=['POST'])
def submit_review():

    customer_email = request.form.get(
        'customer_email',
        ''
    ).strip().lower()

    # Check for existing pending review
    pending_review = Review.query.filter(
        Review.customer_email == customer_email,
        Review.is_approved == False
    ).first()

    if pending_review:
        flash(
            'You already have a review awaiting approval.',
            'warning'
        )
        return redirect(
            url_for('reviews')
        )

    review = Review(
        customer_name=request.form.get(
            'customer_name'
        ),
        customer_email=customer_email,
        rating=int(
            request.form.get('rating')
        ),
        comment=request.form.get(
            'comment'
        ),
        is_approved=False
    )

    db.session.add(review)
    db.session.commit()

    flash(
        'Thank you for your review! It will appear after approval.',
        'success'
    )

    return redirect(
        url_for('reviews')
    )

@app.route('/about')
def about():
    """About Us page - using custom template with owners, team, and gallery"""
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
        msg = Message(
            subject=f"Contact Form: {name}",
            recipients=['nigistme1277@gmail.com'],
            reply_to=email,
            body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        )
        mail.send(msg)
        flash('Your message has been sent. We\'ll get back to you soon!', 'success')
    except:
        flash('Sorry, there was an error sending your message. Please try again.', 'danger')
    
    return redirect(url_for('contact'))

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':

        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()

            reservation_date = datetime.strptime(
                request.form.get('date'),
                '%Y-%m-%d'
            ).date()

            reservation_time = request.form.get('time')
            party_size = int(request.form.get('party_size'))
            special_requests = request.form.get(
                'special_requests'
            )

            # -------------------------
            # Email validation
            # -------------------------
            try:
                validate_email(email)
            except EmailNotValidError:
                flash(
                    'Please enter a valid email address.',
                    'danger'
                )
                return redirect(url_for('reserve'))

            # -------------------------
            # Block disposable emails
            # -------------------------
            domain = email.split('@')[1]

            if domain in BLOCKED_DOMAINS:
                flash(
                    'Temporary email addresses are not allowed.',
                    'danger'
                )
                return redirect(url_for('reserve'))

            # -------------------------
            # Duplicate reservation
            # -------------------------
            duplicate = Reservation.query.filter(
                Reservation.customer_email == email,
                Reservation.reservation_date == reservation_date,
                Reservation.reservation_time == reservation_time
            ).first()

            if duplicate:
                flash(
                    'A reservation already exists for this date and time.',
                    'warning'
                )
                return redirect(url_for('reserve'))

            # -------------------------
            # Cooldown check
            # -------------------------
            recent = Reservation.query.filter(
                Reservation.customer_email == email,
                Reservation.status.in_(['pending']),
                Reservation.created_at >= (
                    datetime.utcnow() -
                    timedelta(hours=1)
                )
            ).first()

            if recent:
                flash(
                    'Please wait before submitting another reservation.',
                    'warning'
                )
                return redirect(url_for('reserve'))

            # -------------------------
            # Save reservation
            # -------------------------
            reservation = Reservation(
                customer_name=name,
                customer_email=email,
                customer_phone=phone,
                reservation_date=reservation_date,
                reservation_time=reservation_time,
                party_size=party_size,
                special_requests=special_requests,
                status='pending'
            )

            db.session.add(reservation)
            db.session.commit()

            # -------------------------
            # Customer Email
            # -------------------------
            try:

                msg = Message(
                    subject="Reservation Request Received - EFFOI Restaurant",
                    recipients=[email]
                )

                msg.html = f"""
                <h2>Thank You For Your Reservation Request</h2>

                <p>Hello <b>{name}</b>,</p>

                <p>We have received your reservation request.</p>

                <ul>
                    <li>Date: {reservation_date}</li>
                    <li>Time: {reservation_time}</li>
                    <li>Party Size: {party_size}</li>
                </ul>

                <p>Status:
                    <b style="color:orange;">
                        Pending Confirmation
                    </b>
                </p>
                """

                mail.send(msg)

            except Exception as e:
                app.logger.error(
                    f"Customer email error: {e}"
                )

            # -------------------------
            # Admin Email
            # -------------------------
            try:

                admin_msg = Message(
                    subject=f"New Reservation: {name}",
                    recipients=[
                        "nigistme1277@gmail.com"
                    ]
                )

                admin_msg.html = f"""
                <h2>New Reservation</h2>

                <p><b>Name:</b> {name}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Phone:</b> {phone}</p>
                <p><b>Date:</b> {reservation_date}</p>
                <p><b>Time:</b> {reservation_time}</p>
                <p><b>Party Size:</b> {party_size}</p>
                """

                mail.send(admin_msg)

            except Exception as e:
                app.logger.error(
                    f"Admin email error: {e}"
                )

            flash(
                'Your reservation request has been submitted successfully.',
                'success'
            )

            return redirect(url_for('index'))

        except Exception as e:

            db.session.rollback()

            app.logger.error(
                f"Reservation error: {e}"
            )

            flash(
                'There was an error processing your reservation.',
                'danger'
            )

            return redirect(url_for('reserve'))

    return render_template('public/reserve.html')

@app.route('/admin/reservations/update/<int:reservation_id>', methods=['POST'])
@admin_required
def admin_update_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'confirmed', 'cancelled']:
        old_status = reservation.status
        reservation.status = new_status
        db.session.commit()
        
        # Send email notification to customer about status change
        if new_status != old_status:
            try:
                status_colors = {
                    'confirmed': '#28a745',
                    'cancelled': '#dc3545',
                    'pending': '#ffc107'
                }
                status_icons = {
                    'confirmed': '✅',
                    'cancelled': '❌',
                    'pending': '⏳'
                }
                
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
                            
                            {f'<p style="color: #28a745;"><strong>✓ Your table has been confirmed! We look forward to serving you.</strong></p>' if new_status == 'confirmed' else ''}
                            {f'<p style="color: #dc3545;"><strong>✗ Your reservation has been cancelled. Please contact us if this was a mistake.</strong></p>' if new_status == 'cancelled' else ''}
                            
                            <p>If you have any questions, please call us at <strong>(240) 660-1337</strong>.</p>
                        </div>
                        <div style="background-color: #8B1E1E; color: white; padding: 15px; text-align: center; font-size: 12px;">
                            <p>8233 Fenton St, Silver Spring, MD 20910 | (240) 660-1337</p>
                        </div>
                    </div>
                    """
                )
                mail.send(msg)
                print(f"✅ Status update email sent to {reservation.customer_email}")
            except Exception as e:
                print(f"❌ Failed to send status update email: {str(e)}")
        
        flash(f'Reservation marked as {new_status}', 'success')
    
    return redirect(url_for('admin_reservations'))

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
        # Handle image upload
        image_file = request.files.get('image')
        image_url = request.form.get('image_url')
        
        if image_file and image_file.filename:
            filename = secure_filename(f"menu_{int(time.time())}_{image_file.filename}")
            upload_dir = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'menu')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            try:
                image_file.save(save_path)
                print(f"Saved menu image to {save_path}")
                image_url = url_for('static', filename=f'uploads/menu/{filename}', _external=True)
            except Exception as e:
                print(f"Failed to save menu image: {e}")
                flash('Failed to save uploaded image. Check server permissions.', 'danger')
                return redirect(url_for('admin_menu'))
        
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
        # Handle image upload
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(f"menu_{int(time.time())}_{image_file.filename}")
            upload_dir = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'menu')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            try:
                image_file.save(save_path)
                print(f"Saved menu image to {save_path}")
                # ensure file was actually written
                if not os.path.exists(save_path):
                    print(f"Menu image not found after save: {save_path}")
                    flash('Uploaded file could not be saved. Check server disk/permissions.', 'danger')
                    return redirect(url_for('admin_menu'))

                # remove previous image file if it exists and was stored in uploads/menu
                try:
                    old_url = item.image_url
                    if old_url:
                        parsed = urlparse(old_url)
                        old_name = os.path.basename(parsed.path)
                        old_path = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'menu', old_name)
                        if os.path.exists(old_path) and old_path != save_path:
                            try:
                                os.remove(old_path)
                                print(f"Removed old menu image: {old_path}")
                            except Exception as e:
                                print(f"Failed to remove old menu image: {e}")
                except Exception as e:
                    print(f"Error while handling old image removal: {e}")

                item.image_url = url_for('static', filename=f'uploads/menu/{filename}', _external=True)
            except Exception as e:
                print(f"Failed to save menu image (edit): {e}")
                flash('Failed to save uploaded image. Check server permissions.', 'danger')
                return redirect(url_for('admin_menu'))
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

# ==================== ADMIN MENU EXPORT/IMPORT ====================
@app.route('/admin/menu/export')
@admin_required
def admin_export_menu():
    return render_template('admin/export_menu.html')

@app.route('/admin/menu/download-json')
@admin_required
def admin_download_menu_json():
    categories = Category.query.all()
    menu_data = []
    
    for category in categories:
        items = []
        for item in category.menu_items:
            items.append({
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'image_url': item.image_url,
                'is_special': item.is_special,
                'is_popular': item.is_popular,
                'is_active': item.is_active,
                'display_order': item.display_order
            })
        
        menu_data.append({
            'category': category.name,
            'display_order': category.display_order,
            'is_active': category.is_active,
            'items': items
        })
    
    response = jsonify(menu_data)
    response.headers['Content-Disposition'] = 'attachment; filename=effoi_menu.json'
    return response

@app.route('/admin/menu/import', methods=['GET', 'POST'])
@admin_required
def admin_import_menu():

    if request.method == 'POST':

        if 'confirm' not in request.form:
            flash('Please confirm this action', 'danger')
            return redirect(url_for('admin_import_menu'))

        json_file = request.files.get('menu_json')

        if not json_file:
            flash('No file uploaded', 'danger')
            return redirect(url_for('admin_import_menu'))

        if not json_file.filename.endswith('.json'):
            flash('Only JSON files are allowed', 'danger')
            return redirect(url_for('admin_import_menu'))

        try:
            menu_data = json.loads(
                json_file.read().decode('utf-8')
            )

            # safer delete
            MenuItem.query.delete(synchronize_session=False)
            Category.query.delete(synchronize_session=False)

            for cat_data in menu_data:

                category = Category(
                    name=cat_data['category'],
                    display_order=cat_data.get('display_order', 0),
                    is_active=cat_data.get('is_active', True)
                )

                db.session.add(category)
                db.session.flush()

                for item_data in cat_data.get('items', []):

                    item = MenuItem(
                        name=item_data['name'],
                        description=item_data.get('description', ''),
                        price=item_data['price'],
                        category_id=category.id,
                        image_url=item_data.get('image_url', ''),
                        is_special=item_data.get('is_special', False),
                        is_popular=item_data.get('is_popular', False),
                        is_active=item_data.get('is_active', True),
                        display_order=item_data.get('display_order', 0)
                    )

                    db.session.add(item)

            db.session.commit()

            flash('Menu imported successfully!', 'success')

        except Exception as e:

            db.session.rollback()

            flash(f'Error importing menu: {str(e)}', 'danger')

        return redirect(url_for('admin_menu'))

    return render_template('admin/import_menu.html')

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
        # Handle image upload
        image_file = request.files.get('image')
        image_url = request.form.get('image_url')
        
        if image_file and image_file.filename:
            filename = secure_filename(f"event_{int(time.time())}_{image_file.filename}")
            upload_dir = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'events')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            try:
                image_file.save(save_path)
                print(f"Saved event image to {save_path}")
                if not os.path.exists(save_path):
                    print(f"Event image not found after save: {save_path}")
                    flash('Uploaded file could not be saved. Check server disk/permissions.', 'danger')
                    return redirect(url_for('admin_events'))
                image_url = url_for('static', filename=f'uploads/events/{filename}', _external=True)
            except Exception as e:
                print(f"Failed to save event image: {e}")
                flash('Failed to save uploaded image. Check server permissions.', 'danger')
                return redirect(url_for('admin_events'))
        
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
        # Handle image upload
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(f"event_{int(time.time())}_{image_file.filename}")
            upload_dir = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'events')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            try:
                image_file.save(save_path)
                print(f"Saved event image to {save_path}")
                if not os.path.exists(save_path):
                    print(f"Event image not found after save: {save_path}")
                    flash('Uploaded file could not be saved. Check server disk/permissions.', 'danger')
                    return redirect(url_for('admin_events'))
                try:
                    old_url = event.image_url
                    if old_url:
                        parsed = urlparse(old_url)
                        old_name = os.path.basename(parsed.path)
                        old_path = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'events', old_name)
                        if os.path.exists(old_path) and old_path != save_path:
                            try:
                                os.remove(old_path)
                                print(f"Removed old event image: {old_path}")
                            except Exception as e:
                                print(f"Failed to remove old event image: {e}")
                except Exception as e:
                    print(f"Error while handling old image removal: {e}")
                event.image_url = url_for('static', filename=f'uploads/events/{filename}', _external=True)
            except Exception as e:
                print(f"Failed to save event image (edit): {e}")
                flash('Failed to save uploaded image. Check server permissions.', 'danger')
                return redirect(url_for('admin_events'))
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

# ==================== ADMIN BLOG ====================
@app.route('/admin/blog')
@admin_required
def admin_blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/blog.html', posts=posts)

@app.route('/admin/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def admin_blog_edit(post_id):
    """Edit/approve blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author_name = request.form.get('author_name')
        author_email = request.form.get('author_email')
        status = request.form.get('status')
        
        if not title:
            flash('Title is required', 'danger')
            return redirect(url_for('admin_blog_edit', post_id=post_id))
        
        if not content:
            flash('Content is required', 'danger')
            return redirect(url_for('admin_blog_edit', post_id=post_id))
        
        if not author_name:
            flash('Author name is required', 'danger')
            return redirect(url_for('admin_blog_edit', post_id=post_id))
        
        post.title = title
        post.content = content
        post.author_name = author_name
        post.author_email = author_email if author_email else None
        post.status = status if status else post.status
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(f"blog_{int(time.time())}_{image_file.filename}")
            upload_dir = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'blog')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            try:
                image_file.save(save_path)
                print(f"Saved blog image to {save_path}")
                if not os.path.exists(save_path):
                    print(f"Blog image not found after save: {save_path}")
                    flash('Uploaded file could not be saved. Check server disk/permissions.', 'danger')
                    return redirect(url_for('admin_blog'))
                try:
                    old_url = post.image_url
                    if old_url:
                        parsed = urlparse(old_url)
                        old_name = os.path.basename(parsed.path)
                        old_path = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'blog', old_name)
                        if os.path.exists(old_path) and old_path != save_path:
                            try:
                                os.remove(old_path)
                                print(f"Removed old blog image: {old_path}")
                            except Exception as e:
                                print(f"Failed to remove old blog image: {e}")
                except Exception as e:
                    print(f"Error while handling old blog image removal: {e}")
                post.image_url = url_for('static', filename=f'uploads/blog/{filename}', _external=True)
            except Exception as e:
                print(f"Failed to save blog image (edit): {e}")
                flash('Failed to save uploaded image. Check server permissions.', 'danger')
                return redirect(url_for('admin_blog'))
        elif request.form.get('image_url'):
            post.image_url = request.form.get('image_url')
        
        try:
            db.session.commit()
            flash('Blog post updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating blog post: {str(e)}', 'danger')
        
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
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

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

# ==================== ADMIN RESERVATIONS ====================
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

# ==================== ADMIN HERO SLIDERS - FIXED ====================
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
            # Use app.root_path to build a reliable path to the frontend static folder
            upload_dir = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'sliders')
            try:
                os.makedirs(upload_dir, exist_ok=True)
            except Exception as e:
                flash(f'Could not create upload directory: {str(e)}', 'danger')
                return redirect(url_for('admin_hero_sliders'))

            save_path = os.path.join(upload_dir, filename)
            try:
                image_file.save(save_path)
                # Use the app static URL for saved files
                image_url = url_for('static', filename=f'uploads/sliders/{filename}', _external=True)
                print(f"Saved slider image to: {save_path}")
            except Exception as e:
                flash(f'Failed to save image: {str(e)}', 'danger')
                return redirect(url_for('admin_hero_sliders'))
        
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
            upload_dir = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'sliders')
            try:
                os.makedirs(upload_dir, exist_ok=True)
            except Exception as e:
                flash(f'Could not create upload directory: {str(e)}', 'danger')
                return redirect(url_for('admin_hero_sliders'))

            save_path = os.path.join(upload_dir, filename)
            try:
                image_file.save(save_path)
                slider.image_url = url_for('static', filename=f'uploads/sliders/{filename}', _external=True)
                print(f"Saved edited slider image to: {save_path}")
            except Exception as e:
                flash(f'Failed to save image: {str(e)}', 'danger')
                return redirect(url_for('admin_hero_sliders'))
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
        upload_dir = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'gallery')
        try:
            os.makedirs(upload_dir, exist_ok=True)
        except Exception as e:
            flash(f'Could not create upload directory: {str(e)}', 'danger')
            return redirect(url_for('admin_gallery'))

        save_path = os.path.join(upload_dir, filename)
        try:
            image_file.save(save_path)
        except Exception as e:
            flash(f'Failed to save image: {str(e)}', 'danger')
            return redirect(url_for('admin_gallery'))

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
        print(f"Saved gallery image to: {save_path}")
    else:
        flash('No image file provided', 'danger')
    
    return redirect(url_for('admin_gallery'))

@app.route('/admin/gallery/delete/<int:image_id>', methods=['POST'])
@admin_required
def admin_delete_gallery(image_id):
    image = GalleryImage.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully', 'success')
    return redirect(url_for('admin_gallery'))

# ==================== ADMIN - TOGGLE SPECIALS ====================
@app.route('/admin/menu/toggle-special/<int:item_id>', methods=['POST'])
@admin_required
def admin_toggle_special(item_id):
    """Toggle menu item special status"""
    item = MenuItem.query.get_or_404(item_id)
    item.is_special = not item.is_special
    db.session.commit()
    flash(f'"{item.name}" {"added to" if item.is_special else "removed from"} specials', 'success')
    return redirect(url_for('admin_specials'))

@app.route('/admin/menu/toggle-popular/<int:item_id>', methods=['POST'])
@admin_required
def admin_toggle_popular(item_id):
    """Toggle menu item popular status"""
    item = MenuItem.query.get_or_404(item_id)
    item.is_popular = not item.is_popular
    db.session.commit()
    flash(f'"{item.name}" {"marked as" if item.is_popular else "unmarked as"} popular', 'success')
    return redirect(url_for('admin_specials'))

@app.route('/admin/specials')
@admin_required
def admin_specials():
    """Manage specials"""
    items = MenuItem.query.order_by(MenuItem.category_id, MenuItem.name).all()
    return render_template('admin/specials.html', items=items)

# ==================== ADMIN - ABOUT PAGE MANAGEMENT ====================
@app.route('/admin/about/edit', methods=['GET', 'POST'])
@admin_required
def admin_about_edit():
    """Edit about page with all components"""
    about = AboutUs.query.first()
    if not about:
        about = AboutUs()
        db.session.add(about)
        db.session.commit()
    
    if request.method == 'POST':
        print("\n=== ABOUT US SAVE DEBUG ===")
        
        # Hero Section
        about.hero_title = request.form.get('hero_title', 'About EFFOI')
        
        # Handle video upload
        video_file = request.files.get('hero_video')
        print(f"Video file received: {video_file}")
        
        if video_file and video_file.filename:
            print(f"Video filename: {video_file.filename}")
            
            # Check file extension
            allowed_extensions = {'mp4', 'webm', 'ogg', 'mov', 'avi'}
            file_ext = video_file.filename.rsplit('.', 1)[1].lower() if '.' in video_file.filename else ''
            
            if file_ext in allowed_extensions:
                # Secure the filename
                filename = secure_filename(video_file.filename)
                filename = f"about_video_{int(time.time())}_{filename}"
                
                # Get the correct path
                project_root = os.path.dirname(os.path.dirname(__file__))
                upload_dir = os.path.join(project_root, 'frontend', 'static', 'uploads', 'about')
                
                # Create directory if it doesn't exist
                os.makedirs(upload_dir, exist_ok=True)
                print(f"Upload directory: {upload_dir}")
                
                # Save the file
                file_path = os.path.join(upload_dir, filename)
                video_file.save(file_path)
                print(f"File saved to: {file_path}")
                
                # Create URL
                about.hero_video_url = url_for('static', filename=f'uploads/about/{filename}')
                print(f"Video URL: {about.hero_video_url}")
            else:
                flash(f'Invalid file type. Allowed: {", ".join(allowed_extensions)}', 'danger')
                
        elif request.form.get('hero_video_url'):
            about.hero_video_url = request.form.get('hero_video_url')
            print(f"Using URL from form: {about.hero_video_url}")
        
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
        
        # IMPORTANT: Remove the old gallery code - we're not saving gallery_images here anymore
        # The gallery is now handled by the separate AJAX routes
        
        try:
            db.session.commit()
            flash('About Us page updated successfully!', 'success')
            print("=== SAVE SUCCESSFUL ===\n")
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving: {str(e)}', 'danger')
            print(f"=== SAVE ERROR: {str(e)} ===\n")
        
        return redirect(url_for('admin_about_edit'))
    
    # Get gallery images from the new model
    gallery_images = AboutUsImage.query.filter_by(about_us_id=about.id, is_active=True).order_by(AboutUsImage.display_order).all()
    
    return render_template('admin/about_edit.html', about=about, gallery_images=gallery_images)

# ==================== ABOUT US GALLERY MANAGEMENT ====================
@app.route('/admin/about/gallery/upload', methods=['POST'])
@admin_required
def admin_about_gallery_upload():
    """Upload images for About Us gallery"""
    about = AboutUs.query.first()
    if not about:
        about = AboutUs()
        db.session.add(about)
        db.session.commit()
    
    files = request.files.getlist('images')
    uploaded_count = 0
    
    for i, file in enumerate(files):
        if file and file.filename:
            # Get title from form
            title = request.form.get(f'title_{i}', '')
            
            # Save file
            filename = secure_filename(file.filename)
            filename = f"about_gallery_{int(time.time())}_{i}_{filename}"
            
            project_root = os.path.dirname(os.path.dirname(__file__))
            upload_dir = os.path.join(project_root, 'frontend', 'static', 'uploads', 'about', 'gallery')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Create image record
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
    """Update image title"""
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
    """Delete image"""
    image = AboutUsImage.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    return jsonify({'success': True})

# ==================== ADMIN EVENT GALLERY ====================
@app.route('/admin/event-gallery/<int:event_id>')
@admin_required
def admin_event_gallery(event_id):
    """Manage gallery images for a specific event"""
    event = Event.query.get_or_404(event_id)
    images = EventImage.query.filter_by(event_id=event_id).order_by(EventImage.display_order).all()
    return render_template('admin/event_gallery.html', event=event, images=images)

@app.route('/admin/event-gallery/upload/<int:event_id>', methods=['POST'])
@admin_required
def admin_upload_event_gallery(event_id):
    """Upload multiple images for an event"""
    event = Event.query.get_or_404(event_id)
    
    files = request.files.getlist('images')
    default_title = request.form.get('default_title', '')
    
    uploaded_count = 0
    
    for file in files:
        if file and file.filename:
            # Create filename
            filename = secure_filename(file.filename)
            filename = f"event_{event_id}_{int(time.time())}_{uploaded_count}_{filename}"
            
            # Save file
            project_root = os.path.dirname(os.path.dirname(__file__))
            upload_dir = os.path.join(project_root, 'frontend', 'static', 'uploads', 'events', 'gallery')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Create database entry
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

@app.route('/admin/event-gallery/update/<int:image_id>', methods=['POST'])
@admin_required
def admin_update_event_gallery(image_id):
    """Update image details"""
    image = EventImage.query.get_or_404(image_id)
    
    data = request.get_json()
    if data and 'title' in data:
        image.title = data['title']
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 400

@app.route('/admin/event-gallery/edit/<int:image_id>', methods=['POST'])
@admin_required
def admin_edit_event_gallery(image_id):
    """Edit image details with optional replacement"""
    image = EventImage.query.get_or_404(image_id)
    
    image.title = request.form.get('title', image.title)
    image.display_order = int(request.form.get('display_order', image.display_order))
    image.is_active = 'is_active' in request.form
    
    # Handle image replacement
    new_image = request.files.get('image')
    if new_image and new_image.filename:
        filename = secure_filename(new_image.filename)
        filename = f"event_{image.event_id}_{int(time.time())}_{filename}"
        
        project_root = os.path.dirname(os.path.dirname(__file__))
        upload_dir = os.path.join(project_root, 'frontend', 'static', 'uploads', 'events', 'gallery')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        new_image.save(file_path)
        
        image.image_url = url_for('static', filename=f'uploads/events/gallery/{filename}', _external=True)
    
    db.session.commit()
    flash('Image updated successfully!', 'success')
    return redirect(url_for('admin_event_gallery', event_id=image.event_id))

@app.route('/admin/event-gallery/delete/<int:image_id>', methods=['POST'])
@admin_required
def admin_delete_event_gallery(image_id):
    """Delete image"""
    image = EventImage.query.get_or_404(image_id)
    event_id = image.event_id
    
    db.session.delete(image)
    db.session.commit()
    
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('admin_event_gallery', event_id=event_id))

# ==================== ADMIN GALLERY EDIT ====================
@app.route('/admin/gallery/edit/<int:image_id>', methods=['POST'])
@admin_required
def admin_edit_gallery(image_id):
    """Edit gallery image"""
    image = GalleryImage.query.get_or_404(image_id)
    
    image.title = request.form.get('title')
    image.category = request.form.get('category')
    image.display_order = int(request.form.get('display_order', 0))
    image.is_active = 'is_active' in request.form
    
    # Handle image upload
    image_file = request.files.get('image')
    if image_file and image_file.filename:
        filename = secure_filename(f"gallery_{int(time.time())}_{image_file.filename}")
        upload_dir = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'gallery')
        try:
            os.makedirs(upload_dir, exist_ok=True)
        except Exception as e:
            flash(f'Could not create upload directory: {str(e)}', 'danger')
            return redirect(url_for('admin_gallery'))

        save_path = os.path.join(upload_dir, filename)
        try:
            image_file.save(save_path)
            image.image_url = url_for('static', filename=f'uploads/gallery/{filename}', _external=True)
            print(f"Saved edited gallery image to: {save_path}")
        except Exception as e:
            flash(f'Failed to save image: {str(e)}', 'danger')
            return redirect(url_for('admin_gallery'))
    
    db.session.commit()
    flash('Image updated successfully', 'success')
    return redirect(url_for('admin_gallery'))

# ==================== API - GET GALLERY IMAGE ====================
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


# ==================== ADMIN - EVENT TOGGLE ====================
@app.route('/admin/events/toggle/<int:event_id>', methods=['POST'])
@admin_required
def admin_toggle_event(event_id):
    """Toggle event active status"""
    event = Event.query.get_or_404(event_id)
    event.is_active = not event.is_active
    db.session.commit()
    flash(f'Event {"activated" if event.is_active else "deactivated"} successfully', 'success')
    return redirect(url_for('admin_events'))

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
    'logo_url': request.form.get('logo_url', 'https://raw.githubusercontent.com/Tesfay-Tesfu/Mella-Technollogy-LLC-Python-Course/main/Effoi_Logo.png'),
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

# ==================== API ENDPOINT ====================
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

# ==================== RUN APPLICATION ====================
if __name__ == '__main__':
    # Create all upload directories
    upload_folders = ['blog', 'sliders', 'events', 'gallery', 'menu', 'about', 'temp']
    project_root = os.path.dirname(os.path.dirname(__file__))
    
    for folder in upload_folders:
        folder_path = os.path.join(project_root, 'frontend', 'static', 'uploads', folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"✅ Created upload folder: {folder_path}")
    
    app.run(debug=True, port=5001)
