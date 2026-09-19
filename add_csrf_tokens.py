import re

files = [
    "frontend/templates/admin/menu_form.html",
    "frontend/templates/admin/hero_slider_form.html",
    "frontend/templates/admin/specials.html",
    "frontend/templates/admin/page_form.html",
    "frontend/templates/admin/faqs.html",
    "frontend/templates/admin/blog.html",
    "frontend/templates/admin/faq_form.html",
    "frontend/templates/admin/import_menu.html",
    "frontend/templates/admin/blog_form.html",
    "frontend/templates/admin/about_edit.html",
    "frontend/templates/admin/menu.html",
    "frontend/templates/admin/reservations.html",
    "frontend/templates/admin/login.html",
    "frontend/templates/admin/gallery.html",
    "frontend/templates/admin/hero_sliders.html",
    "frontend/templates/admin/time_blocks.html",
    "frontend/templates/admin/comments.html",
    "frontend/templates/admin/events.html",
    "frontend/templates/admin/settings.html",
    "frontend/templates/admin/event_gallery.html",
    "frontend/templates/admin/event_form.html",
    "frontend/templates/admin/categories.html",
    "frontend/templates/admin/category_form.html",
    "frontend/templates/public/submit_blog.html",
    "frontend/templates/public/contact.html",
    "frontend/templates/public/blog_post.html",
    "frontend/templates/public/reviews.html",
    "frontend/templates/public/upload_test.html",
    "frontend/templates/public/reserve.html",
]

token_line = '\n    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">'
form_pattern = re.compile(r'(<form\b[^>]*\bmethod\s*=\s*["\']post["\'][^>]*>)', re.IGNORECASE)

total_forms = 0
total_inserted = 0

for path in files:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    forms_found = len(form_pattern.findall(content))
    total_forms += forms_found

    def insert_token(match):
        global total_inserted
        tag = match.group(1)
        total_inserted += 1
        return tag + token_line

    new_content = form_pattern.sub(insert_token, content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"{path}: {forms_found} POST form(s) found, token inserted")

print(f"\nTOTAL: {total_forms} POST forms found, {total_inserted} tokens inserted")
