from effoi_app import app, db, TimeBlock

with app.app_context():
    # Check if TimeBlock model exists
    print("Checking TimeBlock model...")
    
    # Try to create a test block
    try:
        from datetime import datetime, timedelta
        test_block = TimeBlock(
            block_date=datetime.now().date(),
            start_time='12:00',
            end_time='15:00',
            reason='Test Block',
            created_by='test'
        )
        print("✅ TimeBlock model is correctly defined")
    except Exception as e:
        print(f"❌ Error with TimeBlock model: {e}")
    
    # Check if table exists
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\nTables in database: {tables}")
    
    if 'time_blocks' in tables:
        print("✅ time_blocks table exists")
        
        # Count records
        count = TimeBlock.query.count()
        print(f"Records in time_blocks: {count}")
        
        if count > 0:
            print("\nSample records:")
            for block in TimeBlock.query.limit(3).all():
                print(f"  - {block.block_date}: {block.start_time}-{block.end_time} ({block.reason})")
    else:
        print("❌ time_blocks table does not exist - creating it now")
        db.create_all()
        print("✅ Tables created")
