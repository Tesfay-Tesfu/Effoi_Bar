from effoi_app import app, db, TimeBlock
from datetime import datetime, timedelta

with app.app_context():
    # Clear existing time blocks
    TimeBlock.query.delete()
    
    # Add some sample time blocks
    today = datetime.now().date()
    
    blocks = [
        TimeBlock(
            block_date=today + timedelta(days=2),
            start_time='14:00',
            end_time='17:00',
            reason='Private Party',
            created_by='admin'
        ),
        TimeBlock(
            block_date=today + timedelta(days=5),
            start_time='19:00',
            end_time='22:00',
            reason='Live Music Event',
            created_by='admin'
        ),
        TimeBlock(
            block_date=today + timedelta(days=7),
            start_time='12:00',
            end_time='15:00',
            reason='Maintenance',
            created_by='admin'
        ),
    ]
    
    for block in blocks:
        db.session.add(block)
    
    db.session.commit()
    print(f"✅ Added {len(blocks)} sample time blocks")
