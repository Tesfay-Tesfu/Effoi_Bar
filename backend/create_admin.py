from effoi_app import app, db, Admin

with app.app_context():
    # Check if admin exists
    admin = Admin.query.filter_by(username='admin').first()
    if admin:
        print("✅ Admin already exists")
        print(f"Username: admin")
        print("Password: (set during creation)")
    else:
        # Create new admin
        admin = Admin(
            username='admin',
            email='nigistme1277@gmail.com'
        )
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()
        print("✅ New admin created!")
        print("Username: admin")
        print("Password: Admin123!")
