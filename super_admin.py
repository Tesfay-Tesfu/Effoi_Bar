from app import app, db, Admin

SUPER_ADMIN_USERNAME = 'admin'
SUPER_ADMIN_EMAIL = 'superadmin@effoi.com'
SUPER_ADMIN_PASSWORD = 'admin123!'

with app.app_context():
    super_admin = Admin.query.filter_by(is_super=True).first()

    if super_admin:
        print('✅ Super admin already exists')
        print(f'Username: {super_admin.username}')
        print(f'Email: {super_admin.email}')
    else:
        existing_admin = Admin.query.filter(
            (Admin.username == SUPER_ADMIN_USERNAME) | (Admin.email == SUPER_ADMIN_EMAIL)
        ).first()

        if existing_admin:
            existing_admin.username = SUPER_ADMIN_USERNAME
            existing_admin.email = SUPER_ADMIN_EMAIL
            existing_admin.is_super = True
            existing_admin.set_password(SUPER_ADMIN_PASSWORD)
            db.session.commit()
            print('✅ Existing admin promoted to super admin')
            print(f'Username: {existing_admin.username}')
            print(f'Email: {existing_admin.email}')
        else:
            new_admin = Admin(
                username=SUPER_ADMIN_USERNAME,
                email=SUPER_ADMIN_EMAIL,
                is_super=True
            )
            new_admin.set_password(SUPER_ADMIN_PASSWORD)
            db.session.add(new_admin)
            db.session.commit()
            print('✅ New super admin created!')
            print(f'Username: {new_admin.username}')
            print(f'Email: {new_admin.email}')

    print('Password:', SUPER_ADMIN_PASSWORD)
