"""
Embed ComfyUI textures into gaze/index.html.
Patches the texture generation block to use base64 data URIs instead of
Canvas2D procedural gen. Falls back to Canvas2D if Image load fails.
"""
import base64
import os

GAME_SRC = os.path.expanduser("~/gaze/index.html")
TEXTURE_DIR = "/tmp/gaze_textures"

TEXTURES = {
    "stone_wall_tileable": "stone",
    "mirror_wall_tileable": "mirror",
    "door_wall_tileable": "door",
}

def png_to_data_uri(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

def main():
    with open(GAME_SRC) as f:
        html = f.read()

    # Build JS block: create Image, set src, set onload to use it;
    # fallback to genXXX() on error for Canvas2D.
    js_lines = []
    for fname, key in TEXTURES.items():
        path = os.path.join(TEXTURE_DIR, fname + ".png")
        if not os.path.exists(path):
            print(f"  ⏭ Skip {fname} (not found)")
            continue
        uri = png_to_data_uri(path)
        size = os.path.getsize(path) / 1024
        # Set src synchronously; if it fails to be an image, set to fallback
        gen_func = f"gen{key.capitalize()}()"
        js_lines.append(f"""  var _comfy_{key} = new Image();
  _comfy_{key}.onload = function() {{ wallTex["{key}"] = _comfy_{key}; }};
  _comfy_{key}.onerror = function() {{ wallTex["{key}"] = {gen_func} }};
  _comfy_{key}.src = "{uri}";""")
        print(f"  ✅ {fname} → wallTex.{key} ({size:.0f}KB)")

    if not js_lines:
        print("No textures to embed")
        return

    # Find and replace the entire try { ... } block
    old_block = """try {
  wallTex.stone = genStone();
  wallTex.mirror = genMirror();
  wallTex.door = genDoor();
  spriteTex.enemy = genEnemySprite();
  spriteTex.enemyPain = genEnemyPain();
  spriteTex.enemyDead = genEnemyDead();
  spriteTex.pickup = genPickup();
} catch(e) { console.error("Texture gen failed:", e); }"""

    new_block = """try {
  // ComfyUI embedded textures (fallback to Canvas2D on error)
""" + "\n".join(js_lines) + """
  spriteTex.enemy = genEnemySprite();
  spriteTex.enemyPain = genEnemyPain();
  spriteTex.enemyDead = genEnemyDead();
  spriteTex.pickup = genPickup();
} catch(e) { console.error("Texture gen failed:", e); }"""

    if old_block not in html:
        print("ERROR: Could not find texture block to replace")
        return

    html = html.replace(old_block, new_block, 1)

    import tempfile
    fd, tmp = tempfile.mkstemp(suffix=".html")
    os.close(fd)
    with open(tmp, "w") as f:
        f.write(html)

    final_size = os.path.getsize(tmp) / 1024
    print(f"\n  ✅ Wrote {tmp} ({final_size:.0f}KB)")

    # Validate: try parsing as HTML (basic check)
    assert "<!DOCTYPE html>" in html, "Missing DOCTYPE"
    assert "wallTex" in html, "Missing wallTex"
    assert "data:image/png;base64," in html, "Missing embedded textures"
    print("  ✓ Basic validation passed")

if __name__ == "__main__":
    main()
