from effoi_app import app, db, AboutUs
import json

with app.app_context():
    about = AboutUs.query.first()
    
    if about:
        print("✅ About Us record found!")
        print(f"ID: {about.id}")
        print(f"Hero Title: {about.hero_title}")
        print(f"Hero Video URL: {about.hero_video_url}")
        print(f"Card 1: {about.card1_title}")
        print(f"Card 2: {about.card2_title}")
        print(f"Card 3: {about.card3_title}")
        
        # Check gallery images
        if about.gallery_images:
            try:
                gallery = json.loads(about.gallery_images)
                print(f"\nGallery images: {len(gallery)}")
                for i, img in enumerate(gallery):
                    print(f"  Image {i+1}: {img.get('url')}")
            except:
                print("Gallery images: Invalid JSON")
        else:
            print("\nNo gallery images")
    else:
        print("❌ No About Us record found! Creating one...")
        about = AboutUs()
        db.session.add(about)
        db.session.commit()
        print("✅ Created new About Us record")
