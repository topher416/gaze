#!/usr/bin/env python3
"""Re-embed ComfyUI textures at 64x64 into gaze.html"""
import base64
import sys

TEXTURES = {
    "stone_64.png": "stone",
    "mirror_64.png": "mirror",
    "door_64.png": "door",
}

def encode_b64(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def main():
    with open("index.html", "r") as f:
        content = f.read()

    original_size = len(content)
    print(f"Original index.html: {original_size:,} bytes ({original_size/1e6:.1f}MB)")

    for fname, name in TEXTURES.items():
        b64 = encode_b64(f"textures/{fname}")
        new_uri = f"data:image/png;base64,{b64}"
        print(f"  {fname} (resized): {len(new_uri):,} bytes")

        # Find the old URI pattern: wallTex.NAME = new Image(); ... .src = "data:image/png;base64,OLD"
        # The old URIs are 2-3MB each, on the same line. We need to find and replace them.
        # Pattern: wallTex.stone.src = "data:image/png;base64,....VERY LONG....";
        # They all appear in the try block around line 390.
        
        # Use marker approach: find the specific line
        marker = f'wallTex.{name} = new Image(); texturePromises.push(waitForImg(wallTex.{name})); wallTex.{name}.src = "data:image/png;base64,'
        if marker in content:
            # Find the old URI: from the marker until the closing quote
            start = content.index(marker)
            uri_start = start + len(marker)
            # Find the matching closing quote (not escaped)
            # The old URIs are VERY long, but they end with ";
            search_from = uri_start
            # Find ";\n  " pattern after the URI
            end_marker = '";'
            uri_end = content.index(end_marker, search_from)
            old_uri = content[uri_start:uri_end]
            old_len = len(old_uri)
            new_len = len(new_uri)
            content = content[:uri_start] + new_uri + content[uri_end:]
            print(f"  Replaced {name}: {old_len:,} -> {new_len:,} bytes")
        else:
            print(f"  ERROR: Could not find marker for wallTex.{name}")
            sys.exit(1)

    # Update version string
    content = content.replace("v0.4.1", "v0.4.2")

    new_size = len(content)
    print(f"\nNew index.html: {new_size:,} bytes ({new_size/1e6:.1f}MB)")
    print(f"Shrunk by: {(original_size - new_size)/1e6:.1f}MB")

    with open("index.html", "w") as f:
        f.write(content)
    print("Written successfully.")

if __name__ == "__main__":
    main()
