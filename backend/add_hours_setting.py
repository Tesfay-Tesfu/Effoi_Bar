from effoi_app import app, db, SiteSetting

with app.app_context():
    # Check if hours_detailed exists
    setting = SiteSetting.query.filter_by(key='hours_detailed').first()
    if not setting:
        setting = SiteSetting(
            key='hours_detailed',
            value='Monday-Friday:11am-10pm,Saturday:11am-11pm,Sunday:11am-9pm',
            type='text'
        )
        db.session.add(setting)
        db.session.commit()
        print("✅ Added hours_detailed setting")
    else:
        print("✅ hours_detailed setting already exists")
