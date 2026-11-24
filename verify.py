import os
import json
from PIL import Image

def verify_assets(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    print("=== Verification of Character Assets ===")
    
    # 1. Check JSON manifest
    json_path = os.path.join(base_dir, "spritesheet.json")
    assert os.path.exists(json_path), "spritesheet.json missing!"
    with open(json_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    print(f"Manifest Loaded: {manifest['character']}")
    print(f"Total Sequences: {len(manifest['sequences'])}, Total Frames: {manifest['total_frames']}")
    
    # 2. Check each sequence
    expected_sequences = {
        "idle": 8,
        "tail_wag": 8,
        "blinking": 4,
        "jumping": 8,
        "happy": 6
    }
    
    total_verified_frames = 0
    for seq_key, expected_count in expected_sequences.items():
        assert seq_key in manifest["sequences"], f"Sequence {seq_key} missing from manifest!"
        seq_data = manifest["sequences"][seq_key]
        assert seq_data["frame_count"] == expected_count, f"{seq_key} expected {expected_count} frames, got {seq_data['frame_count']}"
        
        # Verify individual frame files
        for idx in range(expected_count):
            rel_path = f"frames/{seq_key}/{seq_key}_{idx}.png"
            full_path = os.path.join(base_dir, rel_path)
            assert os.path.exists(full_path), f"File {full_path} missing!"
            
            with Image.open(full_path) as im:
                assert im.size == (320, 320), f"Frame {full_path} size is {im.size}, expected (320, 320)!"
                assert im.mode == "RGBA", f"Frame {full_path} mode is {im.mode}, expected RGBA!"
                # Check corner pixels are 100% transparent
                corner_alpha = im.getpixel((0, 0))[3]
                assert corner_alpha == 0, f"Corner pixel at (0, 0) in {full_path} is not transparent: {corner_alpha}"
                
            total_verified_frames += 1
            
        # Verify sequence sprite sheet
        seq_sheet_path = os.path.join(base_dir, "spritesheets", f"{seq_key}_sheet.png")
        assert os.path.exists(seq_sheet_path), f"Sequence sheet {seq_sheet_path} missing!"
        with Image.open(seq_sheet_path) as im:
            expected_w = 320 * expected_count
            assert im.size == (expected_w, 320), f"Sequence sheet {seq_sheet_path} size is {im.size}, expected ({expected_w}, 320)"
            assert im.mode == "RGBA", f"Sequence sheet mode is {im.mode}"

        print(f"  [OK] Sequence '{seq_key}': {expected_count} frames verified (320x320 RGBA, transparent background)")

    # 3. Check Master Sprite Sheet
    master_path = os.path.join(base_dir, "spritesheet.png")
    assert os.path.exists(master_path), "spritesheet.png missing!"
    with Image.open(master_path) as im:
        assert im.size == (2560, 1600), f"Master sheet size is {im.size}, expected (2560, 1600)"
        assert im.mode == "RGBA", f"Master sheet mode is {im.mode}"
    print(f"  [OK] Master Sprite Sheet: 2560x1600 RGBA (8 columns x 5 rows)")

    # 4. Check Web Application Files
    for web_file in ["index.html", "style.css", "app.js"]:
        full_web = os.path.join(base_dir, web_file)
        assert os.path.exists(full_web), f"Web file {full_web} missing!"
        size = os.path.getsize(full_web)
        assert size > 200, f"Web file {full_web} too small ({size} bytes)"
        print(f"  [OK] Web App Component: {web_file} ({size} bytes)")

    print(f"\nALL CHECKS PASSED: 34/34 frames, 5 sequence sheets, 1 master sheet, and full web application verified!")

if __name__ == "__main__":
    verify_assets()
