#!/bin/bash
# Force add all images (bypass .gitignore)
git add -f frontend/static/uploads/sliders/.
git add -f frontend/static/uploads/menu/.
git add -f frontend/static/uploads/gallery/.
git add -f frontend/static/uploads/events/.
git add -f frontend/static/uploads/blog/.
git add -f frontend/static/uploads/about/.

echo "Images added. Now run:"
echo "git status"
echo "git commit -m 'Add all local images'"
echo "git push origin main"
