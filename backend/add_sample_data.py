from effoi_app import app, db, Review, Reservation, Event, BlogPost, BlogComment
from datetime import datetime, timedelta
import random

with app.app_context():
    # Add sample reviews
    print("Adding sample reviews...")
    sample_reviews = [
        Review(customer_name='John Smith', rating=5, comment='Amazing food! The Doro Wot was incredible.', is_approved=False),
        Review(customer_name='Sarah Johnson', rating=4, comment='Great atmosphere and friendly staff.', is_approved=False),
        Review(customer_name='Mike Wilson', rating=5, comment='Best Ethiopian food in Silver Spring!', is_approved=False),
        Review(customer_name='Emily Davis', rating=5, comment='The vegetarian combo is outstanding.', is_approved=False),
        Review(customer_name='David Brown', rating=4, comment='Authentic flavors, will come back.', is_approved=False),
    ]
    for review in sample_reviews:
        db.session.add(review)
    
    # Add sample reservations
    print("Adding sample reservations...")
    today = datetime.now().date()
    sample_reservations = [
        Reservation(
            customer_name='John Smith',
            customer_email='john@example.com',
            customer_phone='240-555-0101',
            reservation_date=today + timedelta(days=2),
            reservation_time='19:00',
            party_size=4,
            status='pending'
        ),
        Reservation(
            customer_name='Sarah Johnson',
            customer_email='sarah@example.com',
            customer_phone='240-555-0102',
            reservation_date=today + timedelta(days=3),
            reservation_time='20:00',
            party_size=2,
            status='confirmed'
        ),
        Reservation(
            customer_name='Mike Wilson',
            customer_email='mike@example.com',
            customer_phone='240-555-0103',
            reservation_date=today + timedelta(days=5),
            reservation_time='18:30',
            party_size=6,
            status='pending'
        ),
    ]
    for res in sample_reservations:
        db.session.add(res)
    
    # Add sample events
    print("Adding sample events...")
    sample_events = [
        Event(
            title='Live Ethiopian Music Night',
            description='Enjoy traditional Ethiopian music with our featured artists.',
            event_date=today + timedelta(days=7),
            event_time='20:00',
            location='Main Hall',
            price=10.00,
            is_active=True
        ),
        Event(
            title='Coffee Ceremony Experience',
            description='Experience the traditional Ethiopian coffee ceremony.',
            event_date=today + timedelta(days=10),
            event_time='15:00',
            location='Garden Area',
            price=5.00,
            is_active=True
        ),
        Event(
            title='Cultural Dance Performance',
            description='Watch traditional Ethiopian dance performances.',
            event_date=today + timedelta(days=14),
            event_time='19:30',
            location='Main Hall',
            price=15.00,
            is_active=True
        ),
    ]
    for event in sample_events:
        db.session.add(event)
    
    # Add sample blog comment
    print("Adding sample blog comment...")
    post = BlogPost.query.first()
    if post:
        comment = BlogComment(
            post_id=post.id,
            author_name='Guest User',
            author_email='guest@example.com',
            content='Great post! Thanks for sharing.',
            status='pending'
        )
        db.session.add(comment)
    
    db.session.commit()
    print("✅ Sample data added successfully!")
    print("- Added 5 sample reviews")
    print("- Added 3 sample reservations")
    print("- Added 3 sample events")
    print("- Added 1 sample blog comment")
