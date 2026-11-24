import os
import math
import json
from PIL import Image
from dog_generator import create_dog_frame

def build_all_assets(base_dir=None, frame_size=(320, 320)):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    width, height = frame_size
    frames_dir = os.path.join(base_dir, "frames")
    sheets_dir = os.path.join(base_dir, "spritesheets")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(sheets_dir, exist_ok=True)

    # 1. Define Animation Sequence Parameters
    animations = {}

    # Sequence 1: Idle Breathing (8 frames)
    idle_frames = []
    for i in range(8):
        phase = 2.0 * math.pi * (i / 8.0)
        s = math.sin(phase)
        c = math.cos(phase)
        f = create_dog_frame(
            width=width,
            height=height,
            breath_scale_y=1.0 + 0.035 * s,
            breath_scale_x=1.0 + 0.018 * s,
            head_offset_y=-2.5 * s,
            tail_angle_deg=4.0 * c,
            ear_l_tilt=2.0 * math.sin(phase - 0.4),
            ear_r_tilt=-2.0 * math.sin(phase - 0.4),
            eye_state="open",
            mouth_state="smile",
        )
        idle_frames.append(f)
    animations["idle"] = {
        "title": "Idle Breathing",
        "description": "Gentle rhythmic chest expansion, subtle head bobbing, and relaxed tail sway",
        "frames": idle_frames,
        "default_fps": 8,
        "loop": True
    }

    # Sequence 2: Tail Wagging (8 frames)
    wag_frames = []
    for i in range(8):
        phase = 2.0 * math.pi * (i / 8.0)
        s = math.sin(phase)
        c = math.cos(phase)
        f = create_dog_frame(
            width=width,
            height=height,
            tail_angle_deg=28.0 * s,
            hip_shift_x=-2.2 * s,
            ear_l_tilt=-4.0 * c,
            ear_r_tilt=4.0 * c,
            ear_perk=0.5,
            head_offset_y=-1.0 * abs(s),
            eye_state="open",
            mouth_state="smile",
        )
        wag_frames.append(f)
    animations["tail_wag"] = {
        "title": "Tail Wagging",
        "description": "Energetic sinusoidal tail wagging with natural hip weight transfer and alert ears",
        "frames": wag_frames,
        "default_fps": 12,
        "loop": True
    }

    # Sequence 3: Blinking (4 frames)
    blink_specs = [
        {"eye": "open", "head_y": 0.0, "ear_l": 0.0, "ear_r": 0.0},
        {"eye": "half", "head_y": 0.5, "ear_l": 1.5, "ear_r": -1.5},
        {"eye": "closed", "head_y": 1.2, "ear_l": 2.5, "ear_r": -2.5},
        {"eye": "half", "head_y": 0.5, "ear_l": 1.0, "ear_r": -1.0},
    ]
    blink_frames = []
    for spec in blink_specs:
        f = create_dog_frame(
            width=width,
            height=height,
            eye_state=spec["eye"],
            head_offset_y=spec["head_y"],
            ear_l_tilt=spec["ear_l"],
            ear_r_tilt=spec["ear_r"],
            mouth_state="smile",
        )
        blink_frames.append(f)
    animations["blinking"] = {
        "title": "Blinking",
        "description": "Natural eye blink cycle with eyelid squash and subtle head relaxation",
        "frames": blink_frames,
        "default_fps": 6,
        "loop": True
    }

    # Sequence 4: Jumping (8 frames)
    jump_specs = [
        # Frame 0: Anticipation / Crouch
        {"jump_h": 0.0, "sq_y": 0.88, "sq_x": 1.10, "b_y": 10.0, "h_y": 8.0, "ear_l": -10.0, "ear_r": 10.0, "tail": -10.0, "tuck": 0.0, "mouth": "smile", "tongue": 0.0, "eye": "open"},
        # Frame 1: Launch push-off
        {"jump_h": 14.0, "sq_y": 1.14, "sq_x": 0.90, "b_y": -4.0, "h_y": -4.0, "ear_l": 8.0, "ear_r": -8.0, "tail": 10.0, "tuck": 0.2, "mouth": "smile", "tongue": 0.0, "eye": "open"},
        # Frame 2: Ascending
        {"jump_h": 36.0, "sq_y": 1.06, "sq_x": 0.95, "b_y": 0.0, "h_y": 0.0, "ear_l": 16.0, "ear_r": -16.0, "tail": 20.0, "tuck": 0.7, "mouth": "smile", "tongue": 0.0, "eye": "open"},
        # Frame 3: Apex / Peak
        {"jump_h": 50.0, "sq_y": 0.98, "sq_x": 1.02, "b_y": 0.0, "h_y": 0.0, "ear_l": -8.0, "ear_r": 8.0, "tail": 25.0, "tuck": 0.9, "mouth": "pant", "tongue": 0.4, "eye": "open"},
        # Frame 4: Descending
        {"jump_h": 32.0, "sq_y": 1.08, "sq_x": 0.93, "b_y": 0.0, "h_y": 0.0, "ear_l": 18.0, "ear_r": -18.0, "tail": 15.0, "tuck": 0.4, "mouth": "smile", "tongue": 0.0, "eye": "open"},
        # Frame 5: Touchdown contact
        {"jump_h": 6.0, "sq_y": 0.96, "sq_x": 1.04, "b_y": 2.0, "h_y": 2.0, "ear_l": 5.0, "ear_r": -5.0, "tail": 0.0, "tuck": 0.0, "mouth": "smile", "tongue": 0.0, "eye": "open"},
        # Frame 6: Landing impact squash
        {"jump_h": 0.0, "sq_y": 0.84, "sq_x": 1.14, "b_y": 12.0, "h_y": 10.0, "ear_l": -14.0, "ear_r": 14.0, "tail": -12.0, "tuck": 0.0, "mouth": "smile", "tongue": 0.0, "eye": "open"},
        # Frame 7: Recovery rebound
        {"jump_h": 0.0, "sq_y": 1.02, "sq_x": 0.98, "b_y": -2.0, "h_y": -2.0, "ear_l": 2.0, "ear_r": -2.0, "tail": 2.0, "tuck": 0.0, "mouth": "smile", "tongue": 0.0, "eye": "open"},
    ]
    jump_frames = []
    for spec in jump_specs:
        f = create_dog_frame(
            width=width,
            height=height,
            jump_height=spec["jump_h"],
            squash_factor_y=spec["sq_y"],
            squash_factor_x=spec["sq_x"],
            body_offset_y=spec["b_y"],
            head_offset_y=spec["h_y"],
            ear_l_tilt=spec["ear_l"],
            ear_r_tilt=spec["ear_r"],
            tail_angle_deg=spec["tail"],
            paws_tuck=spec["tuck"],
            mouth_state=spec["mouth"],
            tongue_ext=spec["tongue"],
            eye_state=spec["eye"],
        )
        jump_frames.append(f)
    animations["jumping"] = {
        "title": "Jumping",
        "description": "Full Disney-style cartoon jump cycle with anticipation crouch, squash and stretch, airborne apex, and impact compression",
        "frames": jump_frames,
        "default_fps": 10,
        "loop": True
    }

    # Sequence 5: Happy Expression (6 frames)
    happy_specs = [
        # Frame 0: Smile widening, ears perking
        {"eye": "open", "mouth": "smile", "tongue": 0.0, "perk": 0.3, "h_y": 0.0, "tail": 10.0, "blush": False, "sparkle": False},
        # Frame 1: Mouth opens, tongue out, blush appears
        {"eye": "half", "mouth": "pant", "tongue": 0.45, "perk": 0.6, "h_y": -1.5, "tail": 18.0, "blush": True, "sparkle": False},
        # Frame 2: Max joy! Eyes joyful arc, tongue pant, sparkle
        {"eye": "happy", "mouth": "pant", "tongue": 0.85, "perk": 0.9, "h_y": -3.0, "tail": 28.0, "blush": True, "sparkle": True},
        # Frame 3: Playful pant breath bounce
        {"eye": "happy", "mouth": "pant", "tongue": 0.95, "perk": 1.0, "h_y": -4.0, "tail": 24.0, "blush": True, "sparkle": True},
        # Frame 4: Exhale settling
        {"eye": "happy", "mouth": "pant", "tongue": 0.60, "perk": 0.7, "h_y": -2.0, "tail": 16.0, "blush": True, "sparkle": False},
        # Frame 5: Mouth relaxing toward smile
        {"eye": "open", "mouth": "smile", "tongue": 0.10, "perk": 0.4, "h_y": 0.0, "tail": 8.0, "blush": False, "sparkle": False},
    ]
    happy_frames = []
    for spec in happy_specs:
        f = create_dog_frame(
            width=width,
            height=height,
            eye_state=spec["eye"],
            mouth_state=spec["mouth"],
            tongue_ext=spec["tongue"],
            ear_perk=spec["perk"],
            head_offset_y=spec["h_y"],
            tail_angle_deg=spec["tail"],
            blush=spec["blush"],
            sparkle=spec["sparkle"],
        )
        happy_frames.append(f)
    animations["happy"] = {
        "title": "Happy Expression",
        "description": "Joyful reaction with smiling panting tongue, cute squinting eyes, rosy blush, and sparkling stars",
        "frames": happy_frames,
        "default_fps": 8,
        "loop": True
    }

    # 2. Export Individual PNG Frames
    manifest_data = {
        "character": "Buddy the Cartoon Desktop Dog",
        "frame_width": width,
        "frame_height": height,
        "total_frames": 0,
        "sequences": {},
        "master_spritesheet": {
            "file": "spritesheet.png",
            "columns": 8,
            "rows": 0,
            "width": 0,
            "height": 0,
        }
    }

    # Save individual frames & per-sequence sprite sheets
    for seq_key, seq in animations.items():
        seq_folder = os.path.join(frames_dir, seq_key)
        os.makedirs(seq_folder, exist_ok=True)
        frame_filenames = []
        n_frames = len(seq["frames"])

        # Save individual PNGs
        for idx, frame_img in enumerate(seq["frames"]):
            fname = f"{seq_key}_{idx}.png"
            fpath = os.path.join(seq_folder, fname)
            frame_img.save(fpath, "PNG")
            frame_filenames.append(f"frames/{seq_key}/{fname}")

        # Save horizontal sequence sprite sheet
        seq_sheet = Image.new("RGBA", (width * n_frames, height), (0, 0, 0, 0))
        for idx, frame_img in enumerate(seq["frames"]):
            seq_sheet.paste(frame_img, (idx * width, 0))
        seq_sheet_path = os.path.join(sheets_dir, f"{seq_key}_sheet.png")
        seq_sheet.save(seq_sheet_path, "PNG")

        manifest_data["sequences"][seq_key] = {
            "title": seq["title"],
            "description": seq["description"],
            "frame_count": n_frames,
            "default_fps": seq["default_fps"],
            "loop": seq["loop"],
            "files": frame_filenames,
            "spritesheet": f"spritesheets/{seq_key}_sheet.png",
            "frame_rects": [
                {"x": i * width, "y": 0, "w": width, "h": height} for i in range(n_frames)
            ]
        }
        manifest_data["total_frames"] += n_frames

    # 3. Create Combined Master Sprite Sheet
    # Layout: 8 columns wide, rows as needed (34 frames -> 5 rows: 8 + 8 + 8 + 8 + 2 = 34)
    # Alternatively, 1 row per animation sequence:
    # Row 0: Idle (8 frames)
    # Row 1: Tail Wag (8 frames)
    # Row 2: Blinking (4 frames)
    # Row 3: Jumping (8 frames)
    # Row 4: Happy (6 frames)
    # This row-per-sequence layout is the cleanest industry standard!
    seq_order = ["idle", "tail_wag", "blinking", "jumping", "happy"]
    max_cols = max(len(animations[k]["frames"]) for k in seq_order) # 8 cols
    num_rows = len(seq_order) # 5 rows
    master_w = max_cols * width # 8 * 320 = 2560 px
    master_h = num_rows * height # 5 * 320 = 1600 px

    master_sheet = Image.new("RGBA", (master_w, master_h), (0, 0, 0, 0))

    master_frames_atlas = {}
    for row_idx, seq_key in enumerate(seq_order):
        seq = animations[seq_key]
        atlas_frames = []
        for col_idx, frame_img in enumerate(seq["frames"]):
            px = col_idx * width
            py = row_idx * height
            master_sheet.paste(frame_img, (px, py))
            atlas_frames.append({
                "frame": {"x": px, "y": py, "w": width, "h": height},
                "index": col_idx,
                "sequence": seq_key
            })
        master_frames_atlas[seq_key] = atlas_frames
        # update manifest sequence data with master coordinates
        manifest_data["sequences"][seq_key]["master_rects"] = atlas_frames

    master_sheet_path = os.path.join(base_dir, "spritesheet.png")
    master_sheet.save(master_sheet_path, "PNG")

    manifest_data["master_spritesheet"]["columns"] = max_cols
    manifest_data["master_spritesheet"]["rows"] = num_rows
    manifest_data["master_spritesheet"]["width"] = master_w
    manifest_data["master_spritesheet"]["height"] = master_h

    # 4. Save JSON Manifest
    json_path = os.path.join(base_dir, "spritesheet.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"Successfully generated all {manifest_data['total_frames']} frames!")
    print(f"Master Sprite Sheet saved: {master_sheet_path} ({master_w}x{master_h})")
    print(f"Atlas Metadata JSON saved: {json_path}")
    return manifest_data

if __name__ == "__main__":
    build_all_assets()
