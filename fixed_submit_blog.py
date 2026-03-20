@app.route('/blog/submit', methods=['GET', 'POST'])
def submit_blog():
    """Submit a blog post with image upload"""
    if request.method == 'POST':
        # Handle image upload
        image_file = request.files.get('photo')
        image_url = request.form.get('image_url')
        
        if image_file and image_file.filename:
            # Save uploaded file
            filename = secure_filename(f"blog_{int(time.time())}_{image_file.filename}")
            upload_path = os.path.join('frontend/static/uploads/blog', filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            image_file.save(upload_path)
            image_url = url_for('static', filename=f'uploads/blog/{filename}', _external=True)
        
        post = BlogPost(
            title=request.form.get('title'),
            content=request.form.get('content'),
            author_name=request.form.get('author_name'),
            author_email=request.form.get('author_email'),
            image_url=image_url,
            status='pending'
        )
        db.session.add(post)
        db.session.commit()
        
        # Send notification to admin - FIXED: removed Jinja2 syntax
        try:
            email_html = f"""
            <h2>New Blog Post Submitted</h2>
            <p><strong>Author:</strong> {post.author_name}</p>
            <p><strong>Email:</strong> {post.author_email}</p>
            <p><strong>Title:</strong> {post.title}</p>
            <p><strong>Content:</strong> {post.content[:200]}...</p>
            """
            
            if post.image_url:
                email_html += f'<p><strong>Image:</strong> <img src="{post.image_url}" style="max-width: 200px;"></p>'
            
            email_html += f'<p><a href="{url_for("admin_blog_edit", post_id=post.id, _external=True)}">Review in Admin</a></p>'
            
            msg = Message(
                subject=f"New Blog Post Submitted: {post.title}",
                recipients=['nigistme1277@gmail.com'],
                html=email_html
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email error: {e}")
            pass
        
        flash('Thank you for sharing your experience! Your post will be reviewed shortly.', 'success')
        return redirect(url_for('blog'))
    
    return render_template('public/submit_blog.html')
