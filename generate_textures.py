"""
Batch texture generator for The Gaze.
Queues textures via ComfyUI REST API, monitors progress, saves results.
Usage: python3 generate_textures.py [--sprites] [--walls]
"""
import json
import time
import urllib.request
import urllib.parse
import os
import sys

COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = "/tmp/gaze_textures"
CHECKPOINT = "v1-5-pruned-emaonly.safetensors"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Texture definitions ──────────────────────────────────────────
# Each dict: name, prompt, negative_prompt, width, height, seed, steps, cfg

WALL_TEXTURES = [
    {
        "name": "stone_wall_tileable",
        "prompt": "seamless repeating tileable texture, etched scratchboard engraving style, dark gothic stone wall surface, rectangular stone blocks with carved Latin inscription letters, deep weathered mortar gaps, ancient temple wall, dramatic chiaroscuro shadows, monochromatic with subtle rust-red and gold warm tones, uniform surface, no perspective, no focal point, no horizon, no figures, ps5 era game texture tile",
        "negative": "colorful, cartoon, bright, clean, smooth, low detail, perspective, scene, landscape, people, faces, text, words, letters, writing, horizon, sky, ground, doorway, entryway, focal point, center composition, vignette, text, watermark",
        "width": 1024, "height": 1024,
        "seed": 101, "steps": 28, "cfg": 7.0, "sampler": "euler", "scheduler": "normal"
    },
    {
        "name": "stone_wall_alt_tileable",
        "prompt": "seamless repeating tileable texture, scratchboard etching style, weathered gothic stone wall, carved relief patterns, deep grooved textures, dark aged surface with subtle warm rust highlights, dramatic etching detail, monochromatic with gold undertones, uniform repeating pattern, no perspective, no scene composition, no figures, ps5 game texture tile",
        "negative": "colorful, cartoon, bright, clean, smooth, low detail, perspective, scene, landscape, people, faces, text, words, letters, writing, horizon, sky, ground, doorway, entryway, focal point, text, watermark",
        "width": 1024, "height": 1024,
        "seed": 202, "steps": 28, "cfg": 7.0, "sampler": "euler", "scheduler": "normal"
    },
    {
        "name": "mirror_wall_tileable",
        "prompt": "seamless repeating tileable texture, cracked ornate mirror surface, gothic decorative frame pattern, etched scratchboard style, dark monochromatic with subtle warm tones, dramatic chiaroscuro, cracked glass reflection patterns, ornate baroque mirror frame elements, repeating decorative border, uniform surface, no scene, no perspective, ps5 game texture tile",
        "negative": "colorful, cartoon, bright, clean, smooth, low detail, perspective, scene, landscape, people, faces, text, words, letters, writing, horizon, sky, ground, focal point, text, watermark",
        "width": 1024, "height": 1024,
        "seed": 303, "steps": 28, "cfg": 7.0, "sampler": "euler", "scheduler": "normal"
    },
    {
        "name": "door_wall_tileable",
        "prompt": "seamless repeating tileable texture, ancient ornate gothic door panel, scratchboard etching style, carved wooden door with iron studs and decorative patterns, dark gothic surface with dramatic chiaroscuro, monochromatic with subtle rust and gold tones, repeating panel surface, no perspective, no scene, no figures, ps5 game texture tile",
        "negative": "colorful, cartoon, bright, clean, smooth, low detail, perspective, scene, landscape, people, faces, text, words, letters, writing, horizon, sky, ground, doorway leading somewhere, focal point, text, watermark",
        "width": 1024, "height": 1024,
        "seed": 404, "steps": 28, "cfg": 7.0, "sampler": "euler", "scheduler": "normal"
    },
    {
        "name": "floor_stone_tileable",
        "prompt": "seamless repeating tileable texture, ancient stone floor tiles, etched scratchboard style, worn cobblestone pattern, dark gothic surface with dramatic shadows, monochromatic with subtle warm tones, uniform repeating pattern, no perspective, no scene, no horizon, ps5 game texture tile",
        "negative": "colorful, cartoon, bright, clean, smooth, low detail, perspective, scene, landscape, people, faces, text, words, letters, writing, horizon, sky, doorway, focal point, text, watermark",
        "width": 1024, "height": 1024,
        "seed": 505, "steps": 28, "cfg": 7.0, "sampler": "euler", "scheduler": "normal"
    },
]

SPRITE_TEXTURES = [
    {
        "name": "enemy_reflection",
        "prompt": "etched scratchboard engraving, dark humanoid silhouette figure, gothic horror aesthetic, monochromatic with rust-red highlights, dramatic chiaroscuro, detailed scratchboard hatching lines, mysterious reflection entity, pale ghostly figure in darkness, ps5 game enemy sprite concept art",
        "negative": "colorful, cartoon, bright, happy, clean, smooth, low detail, text, watermark, 3d render, anime",
        "width": 512, "height": 512,
        "seed": 601, "steps": 28, "cfg": 7.0, "sampler": "euler", "scheduler": "normal"
    },
    {
        "name": "enemy_gaze_eye",
        "prompt": "etched scratchboard engraving, giant detailed iris and pupil, gothic horror eye of the gaze, monochromatic with rust-red and gold, dramatic chiaroscuro, scratchboard hatching lines, menacing all-seeing eye, ps5 game enemy sprite concept art",
        "negative": "colorful, cartoon, bright, happy, clean, smooth, low detail, text, watermark, 3d render, anime",
        "width": 512, "height": 512,
        "seed": 602, "steps": 28, "cfg": 7.0, "sampler": "euler", "scheduler": "normal"
    },
    {
        "name": "enemy_mirror_frame",
        "prompt": "etched scratchboard engraving, cracked ornate mirror frame, gothic decorative element, monochromatic with gold and rust tones, dramatic chiaroscuro, scratchboard hatching, baroque cracked mirror enemy, ps5 game concept art",
        "negative": "colorful, cartoon, bright, happy, clean, smooth, low detail, text, watermark, 3d render, anime",
        "width": 512, "height": 512,
        "seed": 603, "steps": 28, "cfg": 7.0, "sampler": "euler", "scheduler": "normal"
    },
    {
        "name": "pickup_desire_orb",
        "prompt": "etched scratchboard engraving, glowing orb collectible, ethereal light sphere, monochromatic with subtle gold highlights, dramatic light rays through darkness, scratchboard style, ps5 game pickup collectible sprite",
        "negative": "colorful, cartoon, bright, neon, clean, smooth, low detail, text, watermark, 3d render, anime, ui element",
        "width": 256, "height": 256,
        "seed": 604, "steps": 28, "cfg": 7.0, "sampler": "euler", "scheduler": "normal"
    },
]

# ── ComfyUI API helpers ──────────────────────────────────────────

def queue_prompt(prompt_data):
    """Send a prompt to ComfyUI queue."""
    data = json.dumps({"prompt": prompt_data}).encode()
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data, 
                                  headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def get_history():
    """Get all prompt history."""
    req = urllib.request.Request(f"{COMFYUI_URL}/history")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def get_queue():
    """Get current queue."""
    req = urllib.request.Request(f"{COMFYUI_URL}/queue")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def build_workflow(tex):
    """Build ComfyUI workflow JSON for a texture."""
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": CHECKPOINT}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": tex["prompt"], "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": tex["negative"], "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": tex["width"], "height": tex["height"], "batch_size": 1}
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": tex["seed"],
                "steps": tex["steps"],
                "cfg": tex["cfg"],
                "sampler_name": tex["sampler"],
                "scheduler": tex["scheduler"],
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"images": ["6", 0], "filename_prefix": tex["name"]}
        }
    }

# ── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    gen_sprites = "--sprites" in sys.argv
    gen_walls = "--walls" in sys.argv
    
    # Default: generate walls if no flag specified
    textures = []
    if gen_walls or (not gen_walls and not gen_sprites):
        textures = WALL_TEXTURES
    if gen_sprites:
        textures = textures + SPRITE_TEXTURES
    
    print(f"=== Generating {len(textures)} textures ===")
    print(f"Checkpoint: {CHECKPOINT}")
    print(f"Output: {OUTPUT_DIR}\n")
    
    # Queue all textures
    prompt_ids = []
    for i, tex in enumerate(textures):
        print(f"  Queueing [{i+1}/{len(textures)}]: {tex['name']} ({tex['width']}x{tex['height']}, seed={tex['seed']})")
        workflow = build_workflow(tex)
        result = queue_prompt(workflow)
        prompt_id = result["prompt_id"]
        prompt_ids.append((prompt_id, tex["name"]))
        time.sleep(0.5)  # Small delay between queue submissions
    
    print(f"\n✅ All {len(textures)} textures queued!")
    print("Monitoring progress...\n")
    
    # Monitor until all complete
    completed = set()
    start = time.time()
    
    while len(completed) < len(prompt_ids):
        history = get_history()
        for pid, name in prompt_ids:
            if pid in completed:
                continue
            if pid in history and history[pid].get("status", {}).get("status_str") == "success":
                completed.add(pid)
                elapsed = time.time() - start
                print(f"  ✅ {name} ({elapsed:.0f}s) — {len(completed)}/{len(prompt_ids)} done")
            elif pid in history and history[pid].get("status", {}).get("status_str") == "error":
                print(f"  ❌ {name} — FAILED")
                completed.add(pid)
        
        queue = get_queue()
        pending = len(queue.get("queue_running", [])) + len(queue.get("queue_pending", []))
        if pending > 0:
            print(f"    ({pending} still processing...)")
        
        time.sleep(5)
    
    total = time.time() - start
    print(f"\n🎉 All textures generated in {total:.0f}s ({total/60:.1f} min)")
    print(f"Check {OUTPUT_DIR} for results")
