from effoi_app import app, db, TimeBlock
from datetime import datetime, timedelta
import json

with app.app_context():
    # First, let's make sure we have some time blocks in the database
    print("Checking time blocks in database...")
    blocks = TimeBlock.query.all()
    print(f"Found {len(blocks)} time blocks")
    
    if len(blocks) == 0:
        print("Adding sample time blocks...")
        today = datetime.now().date()
        
        sample_blocks = [
            TimeBlock(
                block_date=today + timedelta(days=1),
                start_time='18:00',
                end_time='21:00',
                reason='Private Event - Birthday Party',
                created_by='admin'
            ),
            TimeBlock(
                block_date=today + timedelta(days=3),
                start_time='12:00',
                end_time='15:00',
                reason='Restaurant Maintenance',
                created_by='admin'
            ),
            TimeBlock(
                block_date=today + timedelta(days=5),
                start_time='19:00',
                end_time='22:00',
                reason='Live Music Night',
                created_by='admin'
            ),
            TimeBlock(
                block_date=today + timedelta(days=7),
                start_time='14:00',
                end_time='17:00',
                reason='Private Catering Event',
                created_by='admin'
            ),
        ]
        
        for block in sample_blocks:
            db.session.add(block)
        
        db.session.commit()
        print(f"✅ Added {len(sample_blocks)} sample time blocks")
    
    # Now test the API endpoint directly
    print("\nTesting API endpoint...")
    from effoi_app import get_blocked_times
    
    with app.test_request_context():
        response = get_blocked_times()
        data = json.loads(response.get_data(as_text=True))
        print(f"API returned {len(data)} blocks")
        for block in data:
            print(f"  - {block['date']}: {block['start_time']}-{block['end_time']} ({block['reason']})")
