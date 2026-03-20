from effoi_app import app, db, HeroSlider
from datetime import datetime

with app.app_context():
    # Clear existing sliders (optional - remove if you want to keep existing)
    # HeroSlider.query.delete()
    
    # Check if sliders exist
    if HeroSlider.query.count() == 0:
        print("Adding sample hero sliders...")
        
        sliders = [
            HeroSlider(
                title='Welcome to EFFOI',
                subtitle='Experience Authentic Ethiopian Cuisine',
                image_url='https://images.unsplash.com/photo-1517244683847-7456bb63ff54?q=80&w=2070',
                button_text='View Menu',
                button_link='/menu',
                display_order=1,
                is_active=True
            ),
            HeroSlider(
                title='Doro Wot',
                subtitle='Our Signature Spicy Chicken Stew',
                image_url='https://images.unsplash.com/photo-1552566624-52f8b3c8b3c9?q=80&w=2070',
                button_text='Order Now',
                button_link='/menu',
                display_order=2,
                is_active=True
            ),
            HeroSlider(
                title='Live Music Every Weekend',
                subtitle='Enjoy Traditional Ethiopian Music',
                image_url='https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=2070',
                button_text='Events',
                button_link='/events',
                display_order=3,
                is_active=True
            ),
            HeroSlider(
                title='Coffee Ceremony',
                subtitle='Traditional Ethiopian Coffee Experience',
                image_url='https://images.unsplash.com/photo-1551218808-94e220e084d2?q=80&w=2070',
                button_text='Learn More',
                button_link='/about',
                display_order=4,
                is_active=True
            ),
            HeroSlider(
                title='Special Catering',
                subtitle='For Your Special Events',
                image_url='https://images.unsplash.com/photo-1555244162-803834f70033?q=80&w=2070',
                button_text='Contact Us',
                button_link='/contact',
                display_order=5,
                is_active=True
            ),
        ]
        
        for slider in sliders:
            db.session.add(slider)
        
        db.session.commit()
        print(f"✅ Added {len(sliders)} hero sliders")
    else:
        print(f"✅ Found {HeroSlider.query.count()} existing hero sliders")
    
    # Display all sliders
    print("\n📊 Current Hero Sliders:")
    for slider in HeroSlider.query.order_by(HeroSlider.display_order).all():
        print(f"  - {slider.title} (Order: {slider.display_order}, Active: {slider.is_active})")
        print(f"    Image: {slider.image_url}")
