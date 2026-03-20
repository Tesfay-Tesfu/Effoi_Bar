from effoi_app import app, db, TimeBlock
from datetime import datetime, timedelta
import json

with app.app_context():
    # Clear existing blocks
    TimeBlock.query.delete()
    
    # Add test blocks
    today = datetime.now().date()
    
    blocks = [
        TimeBlock(
            block_date=today + timedelta(days=1),
            start_time='18:00',
            end_time='21:00',
            reason='Private Event',
            created_by='admin'
        ),
        TimeBlock(
            block_date=today + timedelta(days=3),
            start_time='12:00',
            end_time='15:00',
            reason='Maintenance',
            created_by='admin'
        ),
        TimeBlock(
            block_date=today + timedelta(days=5),
            start_time='19:00',
            end_time='22:00',
            reason='Live Music',
            created_by='admin'
        ),
    ]
    
    for block in blocks:
        db.session.add(block)
    
    db.session.commit()
    print(f"✅ Added {len(blocks)} test time blocks")
    
    # Test the API
    from effoi_app import get_blocked_times
    with app.test_request_context():
        response = get_blocked_times()
        data = json.loads(response.get_data(as_text=True))
        print(f"\n📊 API Response ({len(data)} blocks):")
        for block in data:
            print(f"  - {block['date']}: {block['start_time']}-{block['end_time']} ({block['reason']})")
