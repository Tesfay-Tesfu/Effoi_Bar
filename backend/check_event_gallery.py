from effoi_app import app, db, EventImage, Event
from datetime import datetime

with app.app_context():
    print("=== EVENT GALLERY CHECK ===\n")
    
    # Check all events
    events = Event.query.all()
    print(f"Total events: {len(events)}")
    
    for event in events:
        print(f"\n📅 Event: {event.title} (ID: {event.id})")
        print(f"  Date: {event.event_date}")
        print(f"  Active: {event.is_active}")
        
        # Check images for this event
        images = EventImage.query.filter_by(event_id=event.id).all()
        print(f"  Gallery images: {len(images)}")
        
        for img in images:
            print(f"    - {img.id}: {img.title}")
            print(f"      URL: {img.image_url}")
            print(f"      Active: {img.is_active}")
    
    # Check if any images exist at all
    total_images = EventImage.query.count()
    print(f"\n📊 TOTAL IMAGES IN DATABASE: {total_images}")
    
    if total_images == 0:
        print("\n❌ No images found! You need to upload some.")
        print("Go to Admin → Club Events → Click the gallery button → Add Images")
