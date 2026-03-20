from effoi_app import app, db

with app.app_context():
    db.create_all()
    print("✅ Created event_images table")
