import os
from effoi_app import app, db, HeroSlider, GalleryImage

with app.app_context():
    # Create upload directory
    upload_dir = os.path.join('frontend', 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    print(f"✅ Upload directory created: {upload_dir}")
    
    # Create tables for new models
    db.create_all()
    print("✅ Database tables created for new models")
    
    # Create sample hero slider if none exists
    if HeroSlider.query.count() == 0:
        slider = HeroSlider(
            title='Welcome to EFFOI',
            subtitle='Experience Authentic Ethiopian Cuisine',
            image_url='https://images.unsplash.com/photo-1517244683847-7456bb63ff54?q=80&w=2070',
            button_text='View Menu',
            button_link='/menu',
            display_order=0,
            is_active=True
        )
        db.session.add(slider)
        db.session.commit()
        print("✅ Sample hero slider created")
    
    # Create sample gallery images
    if GalleryImage.query.count() == 0:
        gallery_samples = [
            {'title': 'Restaurant Interior', 'category': 'restaurant', 'image_url': 'https://images.unsplash.com/photo-1517244683847-7456bb63ff54?q=80&w=2070'},
            {'title': 'Ethiopian Coffee', 'category': 'culture', 'image_url': 'https://images.unsplash.com/photo-1551218808-94e220e084d2?q=80&w=2070'},
            {'title': 'Doro Wot', 'category': 'food', 'image_url': 'https://images.unsplash.com/photo-1552566624-52f8b3c8b3c9?q=80&w=2070'},
            {'title': 'Live Music', 'category': 'events', 'image_url': 'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=2070'},
        ]
        for sample in gallery_samples:
            image = GalleryImage(**sample, display_order=0, is_active=True)
            db.session.add(image)
        db.session.commit()
        print("✅ Sample gallery images created")
    
    print("✅ Media setup complete!")
