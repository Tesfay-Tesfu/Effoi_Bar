# EFFOI Restaurant - Deployment Checklist

## Before Pushing to GitHub

- [ ] All unwanted files cleaned
- [ ] No .db or .sqlite files in repository
- [ ] No .env file committed (only .env.example)
- [ ] .gitignore properly configured
- [ ] requirements.txt includes all dependencies
- [ ] render.yaml is present and correctly configured
- [ ] All template files are in place
- [ ] Static files are in correct directories
- [ ] Upload directories have .gitkeep files

## Git Commands to Run

```bash
# Check status
git status

# Add all files
git add .

# Remove any accidentally staged sensitive files
git reset -- .env
git reset -- *.db
git reset -- __pycache__/

# Commit
git commit -m "Production ready: Deploy to Render with PostgreSQL"

# Push
git push origin main
