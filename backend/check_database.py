from effoi_app import app, db, Category, MenuItem, Review, Reservation, BlogPost, Event, FAQ

with app.app_context():
    print("=== DATABASE STATUS ===\n")
    
    # Check Categories
    categories = Category.query.all()
    print(f"Categories: {len(categories)}")
    for cat in categories:
        print(f"  - {cat.name} (Active: {cat.is_active})")
    
    # Check Menu Items
    items = MenuItem.query.all()
    print(f"\nMenu Items: {len(items)}")
    for item in items[:5]:  # Show first 5
        print(f"  - {item.name} - ${item.price}")
    
    # Check Reviews
    reviews = Review.query.all()
    print(f"\nReviews: {len(reviews)}")
    for rev in reviews:
        print(f"  - {rev.customer_name} - Rating: {rev.rating} - Approved: {rev.is_approved}")
    
    # Check Reservations
    reservations = Reservation.query.all()
    print(f"\nReservations: {len(reservations)}")
    for res in reservations:
        print(f"  - {res.customer_name} - {res.reservation_date} - Status: {res.status}")
    
    # Check Blog Posts
    posts = BlogPost.query.all()
    print(f"\nBlog Posts: {len(posts)}")
    for post in posts:
        print(f"  - {post.title} - Author: {post.author_name} - Status: {post.status}")
    
    # Check Events
    events = Event.query.all()
    print(f"\nEvents: {len(events)}")
    for event in events:
        print(f"  - {event.title} - Date: {event.event_date}")
    
    # Check FAQs
    faqs = FAQ.query.all()
    print(f"\nFAQs: {len(faqs)}")
    for faq in faqs:
        print(f"  - {faq.question[:50]}...")
