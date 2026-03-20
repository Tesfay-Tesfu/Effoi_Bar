from effoi_app import app, db, Category, MenuItem

def populate_menu():
    with app.app_context():
        # First, check if categories exist
        categories = Category.query.all()
        if not categories:
            print("No categories found. Creating categories first...")
            # Create categories
            category_names = [
                'APPETIZERS', 'LUNCH DINNER', 'LAMB', 'VEGETERIAN & FISH', 
                'BREAKFAST', 'SANDWICHES', 'DESERT', 'KIDS', 'COLD BEVERAGES'
            ]
            for i, cat_name in enumerate(category_names):
                cat = Category(name=cat_name, display_order=i, is_active=True)
                db.session.add(cat)
            db.session.commit()
            print(f"✅ Created {len(category_names)} categories")
        
        # Now clear existing menu items (but keep categories)
        MenuItem.query.delete()
        
        # Menu data organized by category
        menu_data = {
            'APPETIZERS': [
                ('Sambusa', 'Crispy pastry filled with seasoned lentils or meat', 8.13),
                ('Effoi Salad', 'Fresh mixed greens with Ethiopian dressing', 16.25),
                ('Tomato Fitfit', 'Traditional Ethiopian tomato salad with injera', 16.25),
            ],
            'LUNCH DINNER': [
                ('Beef Combo', 'Assorted beef dishes served with injera', 48.74),
                ('Doro Wot', 'Spicy chicken stew with hard-boiled eggs', 29.24),
                ('Key Wot', 'Spicy beef stew', 25.99),
                ('Gomen Besega', 'Collard greens with beef', 29.24),
                ('Derek Tibs', 'Pan-fried beef with onions and peppers', 38.99),
                ('Gaslight Tibs', 'Sizzling beef tips with special sauce', 32.49),
                ('Geba Weta Tibs', 'Marinated beef with vegetables', 32.49),
                ('Tibs Firfit', 'Chopped tibs mixed with injera', 29.24),
                ('Quanta Firfir', 'Dried beef with injera', 29.24),
                ('Shifinfin', 'Spicy beef with injera', 40.61),
                ('Bozena', 'Grilled beef special', 29.24),
                ('Pasta with Meat', 'Italian pasta with Ethiopian spiced meat', 29.24),
                ('Lega Tibs', 'Mild beef tibs', 29.24),
                ('Awaze Tibs', 'Spicy tibs with awaze sauce', 30.86),
                ('Goden Tibs', 'Special tibs with vegetables', 34.11),
                ('Zil Zil Tibs', 'Sliced beef with special spices', 30.86),
                ('GoredGored', 'Raw beef cubes with spiced butter', 35.74),
                ('Effoi Special', 'Chef\'s special combination platter', 81.24),
                ('Special Kitfo', 'Seasoned raw beef with spices', 38.99),
                ('Regular Kitfo', 'Traditional kitfo', 29.24),
                ('Ethiopian Injera', 'Traditional sourdough flatbread', 5.69),
            ],
            'LAMB': [
                ('Yebeg Tibs', 'Sautéed lamb with onions and peppers', 29.24),
                ('Yebeg Tibs Awaze', 'Spicy lamb tibs with awaze sauce', 32.49),
                ('Yebeg Kikil', 'Boiled lamb with spices', 34.11),
                ('Yebeg Derek Tibs', 'Pan-fried lamb', 38.99),
                ('Alicha Wot', 'Mild lamb stew', 25.99),
            ],
            'VEGETERIAN & FISH': [
                ('Vegi Combo', 'Assorted vegetarian dishes', 30.86),
                ('Special Veggie Combo', 'Deluxe vegetarian platter', 37.36),
                ('Misr Wot', 'Spicy red lentil stew', 24.36),
                ('Shiro Wot', 'Chickpea flour stew', 27.61),
                ('Pasta With Tomato', 'Pasta with tomato sauce', 24.36),
                ('Pasta with Vegetables', 'Pasta with mixed vegetables', 24.36),
                ('Fish Gulash', 'Fish stew with vegetables', 30.86),
                ('Spicy Asa (Fish) Dullet', 'Spicy fish dish', 30.86),
                ('Fried Fish', 'Crispy fried fish', 22.74),
                ('Asa (Fish) Kitfo', 'Seasoned raw fish', 32.49),
                ('Rice', 'Ethiopian style rice', 25.99),
                ('Ye Tsom (Fasting) Injera Fitfit', 'Fasting injera dish', 24.36),
                ('Telba (Flexseed) Wot', 'Flaxseed stew', 21.11),
                ('Telba (Flexceed) Fitfit', 'Flaxseed with injera', 21.11),
                ('Suf (Sunflower) Fitfit', 'Sunflower seed with injera', 21.11),
                ('Tofu Tibs', 'Sautéed tofu with vegetables', 21.11),
                ('Hlbet', 'Spiced chickpea dish', 32.49),
            ],
            'BREAKFAST': [
                ('Fata', 'Bread with yogurt and honey', 21.11),
                ('Chechebsa', 'Flattened bread with spices and honey', 21.11),
                ('Kenche', 'Ethiopian breakfast porridge', 17.86),
                ('Bula Genfo', 'Porridge made from false banana', 21.11),
                ('Bula Genfo with Kitfo', 'Porridge with kitfo', 30.86),
                ('Scrambled Egg', 'Classic scrambled eggs', 17.86),
                ('Scrambled Egg with Sils', 'Scrambled eggs with sauce', 17.86),
                ('Dulet (Tripa)', 'Spiced minced tripe', 24.36),
                ('Breakfast Combo', 'Complete breakfast platter', 38.99),
                ('Fulle', 'Fava bean dish', 21.11),
            ],
            'SANDWICHES': [
                ('Tilapia Sandwich', 'Crispy tilapia fillet sandwich', 17.88),
                ('Tibs Sandwich', 'Beef tibs sandwich', 19.50),
                ('Kitfo Sandwich', 'Seasoned raw beef sandwich', 19.50),
            ],
            'DESERT': [
                ('Baklava', 'Layered pastry with nuts and honey', 8.13),
                ('Cheesecake', 'Creamy New York style cheesecake', 8.13),
                ('Tiramisu', 'Italian coffee dessert', 8.13),
            ],
            'KIDS': [
                ('Mac and Cheese', 'Creamy macaroni and cheese', 19.50),
                ('Effoi Chicken Wings', 'Crispy chicken wings', 17.88),
                ('French Fries', 'Crispy golden fries', 13.00),
            ],
            'COLD BEVERAGES': [
                ('Coke', 'Classic Coca-Cola', 5.69),
                ('Sprite', 'Lemon-lime soda', 5.69),
                ('Canada Dry', 'Ginger ale', 5.69),
                ('Perrier', 'Sparkling mineral water', 5.69),
                ('Fountain Drinks', 'Assorted fountain sodas', 4.06),
                ('Bottle Water', 'Purified bottled water', 4.86),
            ],
        }
        
        # Add menu items to database
        items_added = 0
        for category_name, items in menu_data.items():
            category = Category.query.filter_by(name=category_name).first()
            if category:
                print(f"Adding items to {category_name}...")
                for i, (name, description, price) in enumerate(items):
                    item = MenuItem(
                        name=name,
                        description=description,
                        price=price,
                        category_id=category.id,
                        is_special=(i < 3),  # First 3 items are specials
                        is_popular=(price > 30),  # Items over $30 are popular
                        is_active=True,
                        display_order=i,
                        image_url=f"https://via.placeholder.com/300x200/8B1E1E/ffffff?text={name.replace(' ', '+')}"
                    )
                    db.session.add(item)
                    items_added += 1
            else:
                print(f"⚠️ Category not found: {category_name}")
        
        db.session.commit()
        print(f"✅ Added {items_added} menu items successfully!")

if __name__ == "__main__":
    populate_menu()
