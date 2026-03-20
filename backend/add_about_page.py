from effoi_app import app, db, Page
from datetime import datetime

about_content = """
<div class="policy-section">
    <p class="lead">Welcome to EFFOI Restaurant & Bar, where authentic Ethiopian cuisine meets warm hospitality in the heart of Silver Spring.</p>
</div>

<h2>Our Story</h2>
<p>Founded in 2010 by Tigist Mengistu and Hiwot Alemu, EFFOI began as a dream to share the rich culinary heritage of Ethiopia with the diverse community of Silver Spring, Maryland. What started as a small family kitchen has grown into one of the most beloved Ethiopian restaurants in the area.</p>

<p>Our name "EFFOI" comes from the Amharic word meaning "to nourish" – which is exactly what we aim to do: nourish our guests with delicious food, warm hospitality, and memorable experiences.</p>

<h2>Our Philosophy</h2>
<p>At EFFOI, we believe that food is more than just sustenance – it's a celebration of culture, community, and tradition. We are committed to:</p>
<ul>
    <li><strong>Authenticity:</strong> Using traditional recipes passed down through generations</li>
    <li><strong>Quality:</strong> Sourcing the freshest ingredients from local suppliers</li>
    <li><strong>Hospitality:</strong> Welcoming every guest like family</li>
    <li><strong>Community:</strong> Giving back to the neighborhood that has supported us</li>
</ul>

<h2>Our Team</h2>
<p>Led by Executive Chef Tigist Mengistu and Hospitality Director Hiwot Alemu, our team of 25+ dedicated professionals brings together culinary expertise from across Ethiopia and beyond. Together, we speak 8 languages and have over 150 years of combined experience in the restaurant industry.</p>

<h2>Our Promise</h2>
<p>When you dine at EFFOI, you can expect:</p>
<ul>
    <li>Authentic Ethiopian flavors prepared with care</li>
    <li>Warm, attentive service</li>
    <li>A clean, comfortable atmosphere</li>
    <li>Consistent quality every time</li>
</ul>

<div class="note-box">
    <i class="fas fa-heart"></i> Thank you for being part of our journey. We look forward to serving you!
</div>
"""

with app.app_context():
    # Check if about page exists
    about_page = Page.query.filter_by(slug='about').first()
    
    if about_page:
        about_page.content = about_content
        about_page.updated_at = datetime.utcnow()
        print("✅ Updated existing About page")
    else:
        about_page = Page(
            slug='about',
            title='About EFFOI Restaurant & Bar',
            content=about_content,
            meta_description='Learn about EFFOI Restaurant & Bar - our story, philosophy, team, and commitment to authentic Ethiopian cuisine in Silver Spring, MD.',
            is_active=True
        )
        db.session.add(about_page)
        print("✅ Created new About page")
    
    db.session.commit()
    
    # Show all pages
    pages = Page.query.all()
    print("\n📄 All Pages:")
    for page in pages:
        print(f"  - {page.slug}: {page.title}")
