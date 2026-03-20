from effoi_app import app, db, Page
from datetime import datetime

policy_content = """
<div class="policy-section">
    <p class="lead">At EFFOI Restaurant & Bar, we are committed to providing an exceptional dining experience for all our guests. Please review our policies below to ensure a pleasant visit.</p>
</div>

<h2>1. Reservations & Cancellations</h2>
<ul>
    <li><strong>Reservation Policy:</strong> We accept reservations for parties of up to 8 guests. For larger groups (9+), please contact us directly at (240) 660-1337 to discuss private dining options.</li>
    <li><strong>Cancellation Policy:</strong> We kindly request a minimum of 24 hours notice for any reservation changes or cancellations. For no-shows or last-minute cancellations (within 2 hours of reservation time), we reserve the right to charge a $25 per person fee.</li>
    <li><strong>Late Arrivals:</strong> Please notify us if you are running late. Your table will be held for 15 minutes past the reservation time, after which it may be released to waiting guests.</li>
    <li><strong>Special Occasions:</strong> If you're celebrating a special occasion, please let us know when booking so we can make your experience extra memorable.</li>
</ul>

<h2>2. Dining Experience</h2>
<ul>
    <li><strong>Dress Code:</strong> We maintain a smart-casual dress code. While we welcome guests in comfortable attire, we kindly request no beachwear, athletic singlets, or excessively casual clothing.</li>
    <li><strong>Dietary Restrictions:</strong> Please inform your server of any food allergies or dietary restrictions before ordering. While we take precautions, cross-contamination may occur in our kitchen.</li>
    <li><strong>Children:</strong> Well-behaved children are always welcome. We offer a dedicated kids menu and high chairs are available upon request.</li>
    <li><strong>Pets:</strong> Only service animals are permitted inside the restaurant. Well-behaved pets are welcome on our outdoor patio.</li>
</ul>

<h2>3. Bar & Alcohol Service</h2>
<ul>
    <li><strong>Age Restriction:</strong> No alcohol will be served to persons under 21 years of age. Valid photo ID is required for all guests who appear under 30.</li>
    <li><strong>Responsible Service:</strong> We are committed to responsible alcohol service. Management reserves the right to refuse service to any guest who appears intoxicated or behaves inappropriately.</li>
    <li><strong>Corkage Fee:</strong> Guests wishing to bring their own wine may do so for a corkage fee of $25 per 750ml bottle (limited to two bottles per table).</li>
    <li><strong>Happy Hour:</strong> Our happy hour specials are available Monday-Friday from 4pm-7pm in the bar area only.</li>
</ul>

<h2>4. Payment & Pricing</h2>
<ul>
    <li><strong>Accepted Payments:</strong> We accept all major credit cards (Visa, Mastercard, American Express, Discover), cash, and contactless payments (Apple Pay, Google Pay).</li>
    <li><strong>Gratuity:</strong> An 18% service charge will be added to parties of 6 or more. Additional gratuity is at your discretion.</li>
    <li><strong>Split Checks:</strong> We can split checks for parties of up to 6 guests. For larger parties, please make arrangements with your server at the beginning of your meal.</li>
    <li><strong>Gift Cards:</strong> Gift cards can be purchased in any denomination at our restaurant or through our website. They are non-refundable and not redeemable for cash.</li>
</ul>

<h2>5. Private Events & Catering</h2>
<ul>
    <li><strong>Event Booking:</strong> For private events and buyouts, a deposit of 50% is required to secure your date. The remaining balance is due 7 days prior to the event.</li>
    <li><strong>Cancellation of Events:</strong> Event cancellations must be made at least 14 days in advance for a full refund of deposit. Cancellations within 14 days will forfeit the deposit.</li>
    <li><strong>Catering:</strong> Catering orders require 48 hours notice. Delivery fees apply based on location and order size.</li>
</ul>

<h2>6. Photography & Social Media</h2>
<ul>
    <li><strong>Personal Photography:</strong> We encourage guests to take photos of their food and drinks for personal use and social media. Please tag us @effoirestaurant.</li>
    <li><strong>Professional Photography:</strong> Professional photography or videography requires prior written consent from management.</li>
    <li><strong>Privacy:</strong> By dining with us, you consent to being photographed or filmed for marketing purposes. Please notify staff if you prefer not to be included.</li>
</ul>

<h2>7. Health & Safety</h2>
<ul>
    <li><strong>Cleanliness:</strong> We maintain the highest standards of cleanliness throughout our establishment. Our team follows strict hygiene protocols.</li>
    <li><strong>Illness:</strong> Guests who are feeling unwell or experiencing symptoms of contagious illness are kindly asked to reschedule their visit.</li>
    <li><strong>Allergens:</strong> While we strive to accommodate all dietary needs, our kitchen handles common allergens. Please exercise caution if you have severe allergies.</li>
</ul>

<h2>8. Lost & Found</h2>
<p>Items left behind are held for 30 days. Please contact us at (240) 660-1337 to inquire about lost items. Valuable items are kept in a secure location and require identification for pickup.</p>

<h2>9. Code of Conduct</h2>
<p>EFFOI Restaurant & Bar is committed to providing a safe, respectful environment for all guests and staff. We reserve the right to refuse service or remove any guest engaging in:</p>
<ul>
    <li>Harassment or discrimination of any kind</li>
    <li>Disruptive or aggressive behavior</li>
    <li>Vandalism or theft</li>
    <li>Illegal activities on premises</li>
</ul>

<div class="note-box">
    <i class="fas fa-info-circle"></i> <strong>Note:</strong> These policies are subject to change without notice. Please check with our staff for the most current information. By dining at EFFOI Restaurant & Bar, you agree to abide by these policies.
</div>

<h2>10. Contact Information</h2>
<p>For questions or concerns regarding any of our policies, please contact us:</p>
<ul>
    <li><strong>Phone:</strong> (240) 660-1337</li>
    <li><strong>Email:</strong> nigistme1277@gmail.com</li>
    <li><strong>Address:</strong> 8233 Fenton St, Silver Spring, MD 20910</li>
    <li><strong>Website:</strong> effoirestaurantandbar.com</li>
</ul>

<p class="text-end mt-5"><em>Last Updated: March 2026</em></p>
"""

with app.app_context():
    # Check if policy page exists
    policy_page = Page.query.filter_by(slug='policy').first()
    
    if policy_page:
        # Update existing policy
        policy_page.content = policy_content
        policy_page.updated_at = datetime.utcnow()
        print("✅ Updated existing Policy page")
    else:
        # Create new policy page
        policy_page = Page(
            slug='policy',
            title='Restaurant & Bar Policies',
            content=policy_content,
            meta_description='EFFOI Restaurant & Bar policies regarding reservations, cancellations, dining experience, bar service, payments, private events, and code of conduct.',
            is_active=True
        )
        db.session.add(policy_page)
        print("✅ Created new Policy page")
    
    db.session.commit()
    
    # Verify
    page = Page.query.filter_by(slug='policy').first()
    print(f"\n📄 Policy Page:")
    print(f"  ID: {page.id}")
    print(f"  Title: {page.title}")
    print(f"  Slug: {page.slug}")
    print(f"  Created: {page.created_at}")
    print(f"  Last Updated: {page.updated_at}")
    print(f"  Content Length: {len(page.content)} characters")
