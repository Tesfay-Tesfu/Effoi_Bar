from effoi_app import app, db, HeroSlider

with app.app_context():
    # Clear existing sliders
    HeroSlider.query.delete()
    
    # Add sample sliders
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
            title='Live Music Every Weekend',
            subtitle='Enjoy Traditional Ethiopian Music',
            image_url='https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=2070',
            button_text='Events',
            button_link='/events',
            display_order=2,
            is_active=True
        ),
        HeroSlider(
            title='Special Catering',
            subtitle='For Your Special Events',
            image_url='https://images.unsplash.com/photo-1555244162-803834f70033?q=80&w=2070',
            button_text='Contact Us',
            button_link='/contact',
            display_order=3,
            is_active=True
        ),
    ]
    
    for slider in sliders:
        db.session.add(slider)
    
    db.session.commit()
    print(f"✅ Added {len(sliders)} hero sliders")
