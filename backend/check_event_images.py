from effoi_app import app, db

with app.app_context():
    # Check if the table exists
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("Tables in database:")
    for table in tables:
        print(f"  - {table}")
    
    if 'event_images' in tables:
        print("\n✅ event_images table exists!")
        
        # Try to import the model
        from effoi_app import EventImage
        count = EventImage.query.count()
        print(f"Number of event images: {count}")
    else:
        print("\n❌ event_images table does NOT exist!")
        print("Creating tables...")
        db.create_all()
        print("✅ Tables created!")
