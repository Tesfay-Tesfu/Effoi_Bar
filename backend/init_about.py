from effoi_app import app, db, AboutUs
import json

with app.app_context():
    # Create table
    db.create_all()
    
    # Check if about us exists
    if AboutUs.query.count() == 0:
        about = AboutUs()
        db.session.add(about)
        db.session.commit()
        print("✅ Created About Us record")
    else:
        print("✅ About Us record already exists")
    
    print("\n📊 About Us content ready for editing at:")
    print("   http://localhost:5001/admin/about/edit")
