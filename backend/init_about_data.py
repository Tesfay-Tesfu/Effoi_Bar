from effoi_app import app, db, AboutUs
import json

with app.app_context():
    # Clear existing (optional - remove if you want to keep existing)
    # AboutUs.query.delete()
    
    about = AboutUs.query.first()
    if not about:
        about = AboutUs()
        db.session.add(about)
    
    # Set test data
    about.hero_title = "About EFFOI Restaurant"
    about.hero_video_url = "https://www.youtube.com/embed/dQw4w9WgXcQ"  # Replace with your video
    
    about.card1_title = "Our Story"
    about.card1_text = "Founded in 2010, EFFOI Restaurant brings the authentic taste of Ethiopia to Silver Spring. Our recipes have been passed down through generations."
    about.card1_color = "danger"
    about.card1_icon = "utensils"
    
    about.card2_title = "Our Philosophy"
    about.card2_text = "We believe in using only the freshest ingredients, traditional cooking methods, and serving with warm Ethiopian hospitality."
    about.card2_color = "warning"
    about.card2_icon = "leaf"
    
    about.card3_title = "Our Promise"
    about.card3_text = "Every dish is prepared with love and care, ensuring an unforgettable dining experience."
    about.card3_color = "success"
    about.card3_icon = "heart"
    
    about.stats_dishes = 100
    about.stats_years = 15
    about.stats_customers = 10000
    about.stats_awards = 25
    
    # Sample gallery images
    gallery = [
        {
            'url': 'https://images.unsplash.com/photo-1517244683847-7456bb63ff54?q=80&w=2070',
            'title': 'Restaurant Interior'
        },
        {
            'url': 'https://images.unsplash.com/photo-1552566624-52f8b3c8b3c9?q=80&w=2070',
            'title': 'Doro Wot'
        },
        {
            'url': 'https://images.unsplash.com/photo-1551218808-94e220e084d2?q=80&w=2070',
            'title': 'Coffee Ceremony'
        },
        {
            'url': 'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=2070',
            'title': 'Live Music'
        }
    ]
    about.gallery_images = json.dumps(gallery)
    
    db.session.commit()
    print("✅ About Us data initialized!")
    
    # Verify
    about = AboutUs.query.first()
    print(f"\n📊 About Us record:")
    print(f"  Hero Title: {about.hero_title}")
    print(f"  Hero Video: {about.hero_video_url}")
    print(f"  Cards: {about.card1_title}, {about.card2_title}, {about.card3_title}")
    print(f"  Gallery: {len(json.loads(about.gallery_images))} images")
