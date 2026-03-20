from effoi_app import app, db, Page

with app.app_context():
    pages = Page.query.all()
    print("=== PAGES IN DATABASE ===\n")
    
    if pages:
        for page in pages:
            print(f"ID: {page.id}")
            print(f"Slug: {page.slug}")
            print(f"Title: {page.title}")
            print(f"Created: {page.created_at}")
            print(f"Content Preview: {page.content[:100]}...")
            print("-" * 50)
    else:
        print("❌ No pages found in database!")
        
    # Specifically check for policy page
    policy = Page.query.filter_by(slug='policy').first()
    if policy:
        print("\n✅ Policy page exists!")
        print(f"Title: {policy.title}")
        print(f"Content length: {len(policy.content)} characters")
    else:
        print("\n❌ Policy page does NOT exist!")
