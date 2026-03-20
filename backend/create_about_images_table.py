from effoi_app import app, db

with app.app_context():
    db.create_all()
    print("✅ Created about_us_images table")
