"""
Hybrid text overlay for Lacanian quotes on AI-generated wall textures.
Reads a PNG from /tmp/gaze_textures/, draws Lacanian text at low opacity,
saves back as new PNG and generates base64 data URI.

Usage: python3 text_overlay.py [texture_name]
  texture_name: stone_wall_tileable, mirror_wall_tileable, etc.
  If no argument: processes all available textures.
"""
import os
import base64
import sys

TEXTURE_DIR = "/tmp/gaze_textures"
OVERLAY_DIR = "/tmp/gaze_textures"  # Save in-place or adjacent

# ── Quote definitions ──────────────────────────────────────────
QUOTE_CONFIGS = {
    "stone_wall_tileable": {
        "quotes": [
            {"text": "Je pense là où je ne suis pas", "x": 280, "y": 420, "size": 38, "rotation": -0.03, "opacity": 0.35},
            {"text": "L'Autre", "x": 600, "y": 200, "size": 32, "rotation": 0.05, "opacity": 0.25},
        ],
        "font": "Georgia, serif",
        "color": "rgba(10, 8, 6, 0.5)",  # Dark text on light etched background
    },
    "stone_wall_alt_tileable": {
        "quotes": [
            {"text": "Le signifié flotte sous le signifiant", "x": 150, "y": 350, "size": 36, "rotation": 0.02, "opacity": 0.3},
        ],
        "font": "Georgia, serif",
        "color": "rgba(10, 8, 6, 0.5)",
    },
    "mirror_wall_tileable": {
        "quotes": [
            {"text": "L'Autre", "x": 400, "y": 480, "size": 48, "rotation": -0.02, "opacity": 0.4},
            {"text": "Que me veux-tu?", "x": 200, "y": 200, "size": 28, "rotation": 0.04, "opacity": 0.3},
        ],
        "font": "Georgia, serif",
        "color": "rgba(184, 68, 42, 0.45)",  # Rust-red text for mirror walls
    },
    "door_wall_tileable": {
        "queries": [  # typo intentional to test
        ],
        "quotes": [
            {"text": "Tu ne veux rien savoir de ton désir", "x": 200, "y": 500, "size": 34, "rotation": -0.01, "opacity": 0.35},
        ],
        "font": "Georgia, serif",
        "color": "rgba(245, 242, 237, 0.3)",  # Light text on dark door
    },
}

DEFAULT_CONFIG = {
    "quotes": [
        {"text": "Il n'y a pas de rapport sexuel", "x": 300, "y": 450, "size": 30, "rotation": 0.03, "opacity": 0.3},
    ],
    "font": "Georgia, serif",
    "color": "rgba(10, 8, 6, 0.5)",
}


def parse_rgba(color_str):
    """Parse CSS-style rgba(r, g, b, a) to Pillow-compatible RGBA tuple."""
    # Handle rgba(r, g, b, alpha) format
    parts = color_str.strip("rgba()").split(",")
    r, g, b = int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip())
    alpha = float(parts[3].strip())
    return (r, g, b, int(alpha * 255))

def add_text_overlay(png_path, config, output_path=None):
    """Add Lacanian text overlay to a texture PNG."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return {"error": "PIL/Pillow not installed", "skipped": True}

    img = Image.open(png_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    quotes = config.get("quotes", [])
    font_family = config.get("font", "Georgia, serif")
    text_color = parse_rgba(config.get("color", "rgba(10, 8, 6, 0.5)"))

    for q in quotes:
        text = q["text"]
        x = q["x"]
        y = q["y"]
        size = q["size"]
        rotation = q.get("rotation", 0)
        opacity = q.get("opacity", 0.3)

        # Try to load a serif font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Georgia.ttf", size)
        except (IOError, OSError):
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Times.ttc", size)
            except (IOError, OSError):
                font = ImageFont.load_default()

        # Create rotated text overlay
        if rotation != 0:
            # Draw on larger canvas, then rotate and paste
            text_layer = Image.new("RGBA", (img.width + 200, img.height + 200), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_layer)
            text_draw.text((200, 200), text, font=font, fill=text_color)

            # Rotate
            text_rotated = text_layer.rotate(rotation * 180 / 3.14159, resample=Image.BICUBIC, expand=True)

            # Adjust position and paste
            paste_x = x - text_rotated.width // 4
            paste_y = y - text_rotated.height // 4
            img.paste(text_rotated, (paste_x, paste_y), text_rotated)
        else:
            draw.text((x, y), text, font=font, fill=text_color)

    if output_path is None:
        base, ext = os.path.splitext(png_path)
        output_path = f"{base}_text{ext}"

    img.save(output_path, "PNG")
    return {"output": output_path, "success": True}


def generate_data_uri(png_path):
    """Convert PNG to base64 data URI."""
    with open(png_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def main():
    texture_name = sys.argv[1] if len(sys.argv) > 1 else None

    if texture_name:
        # Process single texture
        png_path = os.path.join(TEXTURE_DIR, f"{texture_name}.png")
        if not os.path.exists(png_path):
            print(f"ERROR: {png_path} not found")
            return

        config = QUOTE_CONFIGS.get(texture_name, DEFAULT_CONFIG)
        output_path = os.path.join(TEXTURE_DIR, f"{texture_name}_text.png")

        print(f"Processing {texture_name}...")
        result = add_text_overlay(png_path, config, output_path)

        if result.get("skipped"):
            print(f"  ⏭ Skipped: {result['error']}")
            print("  Install Pillow: pip3 install Pillow")
            return

        if result.get("success"):
            print(f"  ✅ Saved: {result['output']}")
            data_uri = generate_data_uri(output_path)
            size_kb = os.path.getsize(output_path) / 1024
            print(f"  📏 Size: {size_kb:.0f}KB")
    else:
        # Process all configured textures
        for name, config in QUOTE_CONFIGS.items():
            png_path = os.path.join(TEXTURE_DIR, f"{name}.png")
            if not os.path.exists(png_path):
                print(f"  ⏭ Skip {name} (PNG not found)")
                continue

            output_path = os.path.join(TEXTURE_DIR, f"{name}_text.png")
            print(f"Processing {name}...")
            result = add_text_overlay(png_path, config, output_path)

            if result.get("skipped"):
                print(f"  ⏭ Skipped: {result['error']}")
                print("  Install Pillow: pip3 install Pillow")
                return

            if result.get("success"):
                print(f"  ✅ {result['output']}")

        print("\n✅ All text overlays applied")


if __name__ == "__main__":
    main()
