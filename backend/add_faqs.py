from effoi_app import app, db, FAQ

with app.app_context():
    # Clear existing FAQs
    FAQ.query.delete()
    
    faqs = [
        {
            'question': 'What are your hours of operation?',
            'answer': 'We are open Monday-Friday 11am-10pm, Saturday 11am-11pm, and Sunday 11am-9pm.',
            'display_order': 1,
            'is_active': True
        },
        {
            'question': 'Do you take reservations?',
            'answer': 'Yes! You can make reservations through our website reservation form or by calling us at (240) 660-1337.',
            'display_order': 2,
            'is_active': True
        },
        {
            'question': 'Do you offer vegetarian/vegan options?',
            'answer': 'Yes, we have an extensive vegetarian section with dishes like Vegi Combo, Misr Wot, and Shiro Wot. Many dishes can be made vegan upon request.',
            'display_order': 3,
            'is_active': True
        },
        {
            'question': 'Is Ethiopian food spicy?',
            'answer': 'We offer a range from mild to very spicy. Dishes like Alicha Wot are mild, while Key Wot and Doro Wot have medium heat. We can adjust spice levels to your preference.',
            'display_order': 4,
            'is_active': True
        },
        {
            'question': 'Do you have gluten-free options?',
            'answer': 'Our injera is traditionally made from teff flour, which is gluten-free. However, cross-contamination is possible. Please inform your server of any allergies.',
            'display_order': 5,
            'is_active': True
        },
        {
            'question': 'Do you offer takeout and delivery?',
            'answer': 'Yes! We offer takeout and delivery through our website and partner apps like DoorDash, UberEats, and Grubhub.',
            'display_order': 6,
            'is_active': True
        },
        {
            'question': 'Can I host a private event?',
            'answer': 'Yes! We offer private dining for groups of 10-50 people. Contact us for special menus and pricing.',
            'display_order': 7,
            'is_active': True
        },
        {
            'question': 'Do you have live music?',
            'answer': 'Yes! We feature live Ethiopian music every Friday and Saturday night. Check our events page for upcoming performances.',
            'display_order': 8,
            'is_active': True
        },
        {
            'question': 'What payment methods do you accept?',
            'answer': 'We accept all major credit cards (Visa, Mastercard, American Express, Discover), cash, and contactless payments.',
            'display_order': 9,
            'is_active': True
        },
        {
            'question': 'Do you offer gift cards?',
            'answer': 'Yes! You can purchase gift cards in any denomination at our restaurant or through our website.',
            'display_order': 10,
            'is_active': True
        }
    ]
    
    for faq_data in faqs:
        faq = FAQ(**faq_data)
        db.session.add(faq)
    
    db.session.commit()
    print(f"✅ Added {len(faqs)} FAQs to database")
