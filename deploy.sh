#!/bin/bash
set -e

echo "=== The Gaze — Deploy Script ==="
echo ""

# ─── Step 1: Verify GitHub auth ───
echo "[1/5] Checking GitHub auth..."
ACCOUNT=$(gh auth status 2>&1 | grep "Logged in to" | grep -o "topher416\|thtopher" | head -1)
if [ "$ACCOUNT" != "topher416" ]; then
    echo "  ⚠ Switching to topher416..."
    gh auth switch -u topher416
fi

# Set credential helper if not already set
cd ~/gaze
CRED=$(git config --local --get credential.helper 2>/dev/null || true)
if [ "$CRED" != "!gh auth git-credential" ]; then
    git config --local credential.helper ""
    git config --local --add credential.helper "!gh auth git-credential"
fi

# ─── Step 2: Embed textures if present ───
echo "[2/5] Embedding textures..."
TEXTURE_COUNT=$(ls /tmp/gaze_textures/*.png 2>/dev/null | wc -l | tr -d ' ')
if [ "$TEXTURE_COUNT" -gt 0 ]; then
    echo "  Found $TEXTURE_COUNT textures in /tmp/gaze_textures/"
    python3 ~/gaze/embed_textures.py
else
    echo "  No new textures found, using existing embedded assets"
fi

# ─── Step 3: Push to gaze repo ───
echo "[3/5] Pushing to topher416/gaze..."
cd ~/gaze
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
git add -A
if git diff --cached --quiet; then
    echo "  No changes to commit"
else
    git commit -m "v0.2.1: updated textures $TIMESTAMP"
    git push origin main
    echo "  ✅ Pushed to gaze repo"
fi

# ─── Step 4: Sync to personal site repo ───
echo "[4/5] Syncing to personal site..."
cp ~/gaze/index.html /tmp/personal-site/gaze.html
cd /tmp/personal-site

# Verify auth again for this repo
ACCOUNT=$(gh auth status 2>&1 | grep "Logged in to" | grep -o "topher416\|thtopher" | head -1)
if [ "$ACCOUNT" != "topher416" ]; then
    gh auth switch -u topher416
fi

CRED=$(git config --local --get credential.helper 2>/dev/null || true)
if [ "$CRED" != "!gh auth git-credential" ]; then
    git config --local credential.helper ""
    git config --local --add credential.helper "!gh auth git-credential"
fi

git add gaze.html
if git diff --cached --quiet; then
    echo "  No changes to commit in personal site"
else
    git commit -m "sync gaze v0.2.1 $TIMESTAMP"
    git push origin main
    echo "  ✅ Pushed to personal-site repo"
fi

# ─── Step 5: Verify ───
echo "[5/5] Verifying deployment..."
echo "  Checking raw GitHub..."
RAW_CONTENT=$(curl -s "https://raw.githubusercontent.com/topher416/gaze/main/index.html")
if echo "$RAW_CONTENT" | grep -q "v0.2.1"; then
    echo "  ✅ Raw GitHub has latest version"
else
    echo "  ⚠ Raw GitHub may not have synced yet"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "  Deployed: $TIMESTAMP"
echo "  Check: https://topherrasmussen.com/gaze.html"
echo "  CDN may lag 5-15 minutes. Force refresh: Cmd+Shift+R"
echo "═══════════════════════════════════════════════"
