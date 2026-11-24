import os
import math
import json
from PIL import Image, ImageDraw

def quadratic_bezier(p0, p1, p2, t):
    x = (1 - t)**2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
    y = (1 - t)**2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
    return (x, y)

def cubic_bezier(p0, p1, p2, p3, t):
    x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
    y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1]
    return (x, y)

def sample_curve(points, n=16):
    res = []
    if len(points) == 3:
        p0, p1, p2 = points
        for i in range(n + 1):
            t = i / float(n)
            res.append(quadratic_bezier(p0, p1, p2, t))
    elif len(points) == 4:
        p0, p1, p2, p3 = points
        for i in range(n + 1):
            t = i / float(n)
            res.append(cubic_bezier(p0, p1, p2, p3, t))
    return res

def create_dog_frame(
    width=320,
    height=320,
    scale_factor=4,
    # Animation parameters
    breath_scale_y=1.0,
    breath_scale_x=1.0,
    head_offset_y=0.0,
    head_tilt_deg=0.0,
    body_offset_y=0.0,
    tail_angle_deg=0.0,   # -30 to +30 deg wag
    ear_l_tilt=0.0,
    ear_r_tilt=0.0,
    ear_perk=0.0,         # 0.0 to 1.0 (happy perk)
    eye_state="open",     # "open", "half", "closed", "happy"
    mouth_state="smile",  # "smile", "open", "pant"
    tongue_ext=0.0,       # 0.0 to 1.0
    jump_height=0.0,      # in pixels (0 to 60)
    squash_factor_y=1.0,  # 0.80 to 1.20
    squash_factor_x=1.0,  # 0.85 to 1.20
    paws_tuck=0.0,        # 0.0 to 1.0 (tuck paws up during airborne)
    blush=False,
    sparkle=False,
    hip_shift_x=0.0,
):
    W = width * scale_factor
    H = height * scale_factor
    S = scale_factor

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    # Character Color Palette: High consistency across all frames
    COAT_MAIN = (255, 179, 56, 255)       # Golden amber fur (#FFB338)
    COAT_SHADOW = (235, 145, 26, 255)     # Warm caramel depth (#EB911A)
    COAT_DARK = (212, 118, 30, 255)       # Rich chestnut caramel (#D4761E)
    COAT_LIGHT = (255, 248, 235, 255)     # Creamy ivory (#FFF8EB)
    OUTLINE = (38, 24, 18, 255)           # Crisp dark espresso (#261812)
    COLLAR_RED = (235, 50, 45, 255)       # Bright red collar (#EB322D)
    GOLD_TAG = (255, 215, 0, 255)         # Vibrant gold bell tag (#FFD700)
    GOLD_OUTLINE = (195, 145, 0, 255)
    NOSE_BLACK = (28, 24, 22, 255)        # Button nose (#1C1816)
    EYE_DARK = (26, 20, 18, 255)
    EYE_IRIS = (115, 75, 48, 255)
    MOUTH_DARK = (115, 24, 38, 255)
    TONGUE = (255, 115, 142, 255)
    TONGUE_SHADOW = (225, 80, 110, 255)
    BLUSH = (255, 130, 130, 120)

    OUTLINE_W = int(4.5 * S)
    THIN_W = int(2.5 * S)

    # Reference Ground Plane & Jump Physics
    ground_y = 265 * S
    total_dy = -(jump_height * S) + (body_offset_y * S)

    # 1. Contact Shadow on ground
    shadow_scale = max(0.25, (1.0 - (jump_height / 75.0) * 0.45) * squash_factor_x)
    shadow_alpha = int(max(25, 75 * (1.0 - (jump_height / 75.0) * 0.70)))
    sw = int(72 * S * shadow_scale)
    sh = int(14 * S * shadow_scale)
    draw.ellipse([160 * S - sw, ground_y - sh // 2 + int(4*S), 160 * S + sw, ground_y + sh + int(4*S)], fill=(20, 15, 10, shadow_alpha))

    # Base Centers
    body_cx = (160 * S) + int(hip_shift_x * S)
    body_cy = (185 * S) + total_dy
    hip_y = (220 * S) + total_dy

    # 2. Tail (Visible on the right side, wagging smoothly with fluffy tip)
    tail_root_x = body_cx + int(36 * S * squash_factor_x)
    tail_root_y = hip_y - int(8 * S)

    # Wag angle: oscillates between ~ -25 deg and +35 deg
    wag_rad = math.radians(25 + tail_angle_deg)
    tail_len = 65 * S
    t_tip_x = tail_root_x + int(tail_len * math.cos(wag_rad))
    t_tip_y = tail_root_y - int(tail_len * math.sin(wag_rad))
    t_ctrl_x = (tail_root_x + t_tip_x) // 2 + int(12 * S * math.sin(wag_rad))
    t_ctrl_y = min(tail_root_y, t_tip_y) - int(24 * S)

    tail_top = sample_curve([(tail_root_x - int(5*S), tail_root_y - int(12*S)),
                             (t_ctrl_x - int(8*S), t_ctrl_y - int(8*S)),
                             (t_tip_x - int(6*S), t_tip_y)], 16)
    tail_end = sample_curve([(t_tip_x - int(6*S), t_tip_y),
                            (t_tip_x + int(5*S), t_tip_y - int(5*S)),
                            (t_tip_x + int(8*S), t_tip_y + int(4*S))], 8)
    tail_bot = sample_curve([(t_tip_x + int(8*S), t_tip_y + int(4*S)),
                             (t_ctrl_x + int(10*S), t_ctrl_y + int(12*S)),
                             (tail_root_x + int(8*S), tail_root_y + int(8*S))], 16)
    tail_poly = tail_top + tail_end + tail_bot
    draw.polygon(tail_poly, fill=COAT_MAIN)

    # Cream tail tip (smoothly clipped inside tail polygon)
    tip_start_top = int(len(tail_top) * 0.65)
    tip_end_bot = int(len(tail_bot) * 0.35)
    tip_poly = tail_top[tip_start_top:] + tail_end + tail_bot[:tip_end_bot]
    draw.polygon(tip_poly, fill=COAT_LIGHT)
    draw.line(tail_poly + [tail_poly[0]], fill=OUTLINE, width=OUTLINE_W, joint="curve")

    # 3. Back Haunches (Seated dog hips, lifting realistically when jumping)
    for side in (-1, 1):
        haunch_cx = body_cx + side * int(48 * S * squash_factor_x)
        haunch_cy = hip_y - int(2 * S)
        hw = int(24 * S * squash_factor_x)
        hh = int(28 * S * squash_factor_y)
        draw.ellipse([haunch_cx - hw, haunch_cy - hh, haunch_cx + hw, haunch_cy + hh], fill=COAT_SHADOW, outline=OUTLINE, width=OUTLINE_W)

    # 4. Back Paws (Move up synchronously during jump!)
    for side in (-1, 1):
        bp_cx = body_cx + side * int(56 * S * squash_factor_x)
        bp_cy = (ground_y - int(10 * S)) + total_dy - int(paws_tuck * 16 * S)
        bp_w = int(20 * S * squash_factor_x)
        bp_h = int(12 * S * squash_factor_y)
        draw.ellipse([bp_cx - bp_w, bp_cy - bp_h, bp_cx + bp_w, bp_cy + bp_h], fill=COAT_MAIN, outline=OUTLINE, width=OUTLINE_W)
        draw.line([bp_cx - int(5*S), bp_cy - bp_h + int(4*S), bp_cx - int(5*S), bp_cy + bp_h - int(2*S)], fill=OUTLINE, width=THIN_W)
        draw.line([bp_cx + int(5*S), bp_cy - bp_h + int(4*S), bp_cx + int(5*S), bp_cy + bp_h - int(2*S)], fill=OUTLINE, width=THIN_W)

    # 5. Main Body
    b_w = int(50 * S * squash_factor_x * breath_scale_x)
    b_h = int(58 * S * squash_factor_y * breath_scale_y)
    body_bbox = [body_cx - b_w, body_cy - b_h, body_cx + b_w, hip_y + int(10 * S * squash_factor_y)]
    draw.chord(body_bbox, start=0, end=360, fill=COAT_MAIN, outline=OUTLINE, width=OUTLINE_W)

    # 6. Front Legs (Organic rounded legs blending down to paws)
    leg_w = int(12 * S * squash_factor_x)
    leg_top_y = body_cy + int(10 * S)
    leg_bot_y = (ground_y - int(10 * S)) + total_dy - int(paws_tuck * 22 * S)

    for side in (-1, 1):
        leg_cx = body_cx + side * int(18 * S * squash_factor_x)
        draw.polygon([
            (leg_cx - leg_w, leg_top_y),
            (leg_cx - leg_w, leg_bot_y),
            (leg_cx + leg_w, leg_bot_y),
            (leg_cx + leg_w, leg_top_y)
        ], fill=COAT_MAIN)
        draw.line([(leg_cx - leg_w, leg_top_y), (leg_cx - leg_w, leg_bot_y)], fill=OUTLINE, width=OUTLINE_W)
        draw.line([(leg_cx + leg_w, leg_top_y), (leg_cx + leg_w, leg_bot_y)], fill=OUTLINE, width=OUTLINE_W)

        # Front Paws (Cream colored with clean toe dividers)
        fp_w = int(16 * S * squash_factor_x)
        fp_h = int(12 * S * squash_factor_y)
        draw.ellipse([leg_cx - fp_w, leg_bot_y - fp_h, leg_cx + fp_w, leg_bot_y + fp_h], fill=COAT_LIGHT, outline=OUTLINE, width=OUTLINE_W)
        draw.line([leg_cx - int(5*S), leg_bot_y - fp_h + int(3*S), leg_cx - int(5*S), leg_bot_y + fp_h - int(2*S)], fill=OUTLINE, width=THIN_W)
        draw.line([leg_cx + int(5*S), leg_bot_y - fp_h + int(3*S), leg_cx + int(5*S), leg_bot_y + fp_h - int(2*S)], fill=OUTLINE, width=THIN_W)

    # 7. Chest/Belly Cream Patch (Layered cleanly over legs for seamless transition)
    ch_w = int(28 * S * squash_factor_x * breath_scale_x)
    ch_h = int(46 * S * squash_factor_y * breath_scale_y)
    draw.ellipse([body_cx - ch_w, body_cy - int(12*S), body_cx + ch_w, body_cy + ch_h], fill=COAT_LIGHT)

    # 8. Collar & Golden Tag
    head_cx = body_cx
    head_cy = (124 * S) + total_dy + (head_offset_y * S)
    
    col_w = int(36 * S * squash_factor_x)
    col_h = int(12 * S)
    col_cx = body_cx
    col_cy = head_cy + int(42 * S * squash_factor_y)
    draw.ellipse([col_cx - col_w, col_cy - col_h, col_cx + col_w, col_cy + col_h], fill=COLLAR_RED, outline=OUTLINE, width=OUTLINE_W)
    
    # Golden Bell Tag
    tag_r = int(9 * S)
    tag_cy = col_cy + int(9 * S)
    draw.ellipse([col_cx - tag_r, tag_cy - tag_r, col_cx + tag_r, tag_cy + tag_r], fill=GOLD_TAG, outline=GOLD_OUTLINE, width=THIN_W)
    draw.ellipse([col_cx - tag_r, tag_cy - tag_r, col_cx + tag_r, tag_cy + tag_r], outline=OUTLINE, width=OUTLINE_W)
    draw.ellipse([col_cx - int(2*S), tag_cy + int(2*S), col_cx + int(2*S), tag_cy + int(5*S)], fill=OUTLINE)
    draw.ellipse([col_cx - int(4*S), tag_cy - int(4*S), col_cx - int(1*S), tag_cy - int(1*S)], fill=(255, 255, 255, 230))

    # 9. Floppy Ears
    # Left Ear
    e_l_ang = math.radians(-10 + ear_l_tilt - ear_perk * 22)
    e_l_root_x = head_cx - int(42 * S)
    e_l_root_y = head_cy - int(24 * S)
    e_l_tip_x = e_l_root_x - int(36 * S * math.cos(e_l_ang)) + int(10 * S * math.sin(e_l_ang))
    e_l_tip_y = e_l_root_y + int(58 * S * math.cos(e_l_ang)) + int(18 * S * math.sin(e_l_ang))
    
    ear_l_pts = sample_curve([(e_l_root_x, e_l_root_y), (e_l_root_x - int(34*S), e_l_root_y + int(16*S)), (e_l_tip_x - int(8*S), e_l_tip_y - int(8*S))], 12) + \
                sample_curve([(e_l_tip_x - int(8*S), e_l_tip_y - int(8*S)), (e_l_tip_x, e_l_tip_y + int(8*S)), (e_l_tip_x + int(16*S), e_l_tip_y)], 8) + \
                sample_curve([(e_l_tip_x + int(16*S), e_l_tip_y), (e_l_root_x + int(4*S), e_l_root_y + int(30*S)), (e_l_root_x + int(12*S), e_l_root_y + int(8*S))], 12)
    draw.polygon(ear_l_pts, fill=COAT_DARK)
    draw.line(ear_l_pts + [ear_l_pts[0]], fill=OUTLINE, width=OUTLINE_W, joint="curve")

    # Right Ear
    e_r_ang = math.radians(10 + ear_r_tilt + ear_perk * 22)
    e_r_root_x = head_cx + int(42 * S)
    e_r_root_y = head_cy - int(24 * S)
    e_r_tip_x = e_r_root_x + int(36 * S * math.cos(e_r_ang)) + int(10 * S * math.sin(e_r_ang))
    e_r_tip_y = e_r_root_y + int(58 * S * math.cos(e_r_ang)) - int(18 * S * math.sin(e_r_ang))

    ear_r_pts = sample_curve([(e_r_root_x, e_r_root_y), (e_r_root_x + int(34*S), e_r_root_y + int(16*S)), (e_r_tip_x + int(8*S), e_r_tip_y - int(8*S))], 12) + \
                sample_curve([(e_r_tip_x + int(8*S), e_r_tip_y - int(8*S)), (e_r_tip_x, e_r_tip_y + int(8*S)), (e_r_tip_x - int(16*S), e_r_tip_y)], 8) + \
                sample_curve([(e_r_tip_x - int(16*S), e_r_tip_y), (e_r_root_x - int(4*S), e_r_root_y + int(30*S)), (e_r_root_x - int(12*S), e_r_root_y + int(8*S))], 12)
    draw.polygon(ear_r_pts, fill=COAT_DARK)
    draw.line(ear_r_pts + [ear_r_pts[0]], fill=OUTLINE, width=OUTLINE_W, joint="curve")

    # 10. Head Base
    head_w = int(58 * S * squash_factor_x)
    head_h = int(50 * S * squash_factor_y)
    draw.ellipse([head_cx - head_w, head_cy - head_h, head_cx + head_w, head_cy + head_h], fill=COAT_MAIN, outline=OUTLINE, width=OUTLINE_W)

    # Hair tuft
    tuft = sample_curve([(head_cx - int(12*S), head_cy - head_h + int(4*S)),
                         (head_cx - int(5*S), head_cy - head_h - int(14*S)),
                         (head_cx, head_cy - head_h - int(4*S))], 8) + \
           sample_curve([(head_cx, head_cy - head_h - int(4*S)),
                         (head_cx + int(5*S), head_cy - head_h - int(16*S)),
                         (head_cx + int(12*S), head_cy - head_h + int(4*S))], 8)
    draw.polygon(tuft, fill=COAT_MAIN)
    draw.line(tuft, fill=OUTLINE, width=OUTLINE_W, joint="curve")

    # 11. Muzzle
    muz_cx = head_cx
    muz_cy = head_cy + int(16 * S)
    muz_w = int(38 * S * squash_factor_x)
    muz_h = int(25 * S * squash_factor_y)
    draw.ellipse([muz_cx - muz_w, muz_cy - muz_h, muz_cx + muz_w, muz_cy + muz_h], fill=COAT_LIGHT, outline=OUTLINE, width=OUTLINE_W)

    # 12. Nose
    nose_cx = head_cx
    nose_cy = muz_cy - int(10 * S)
    nose_w = int(13 * S)
    nose_h = int(9 * S)
    draw.ellipse([nose_cx - nose_w, nose_cy - nose_h, nose_cx + nose_w, nose_cy + nose_h], fill=NOSE_BLACK)
    draw.ellipse([nose_cx - int(6*S), nose_cy - int(5*S), nose_cx - int(2*S), nose_cy - int(2*S)], fill=(255, 255, 255, 230))

    # 13. Mouth & Tongue
    mouth_cy = nose_cy + int(12 * S)
    if mouth_state in ("open", "pant"):
        mo_w = int(18 * S)
        mo_h = int(18 * S)
        m_poly = sample_curve([(head_cx - mo_w, mouth_cy), (head_cx, mouth_cy + mo_h + int(6*S)), (head_cx + mo_w, mouth_cy)], 16)
        draw.polygon([(head_cx - mo_w, mouth_cy)] + m_poly + [(head_cx + mo_w, mouth_cy)], fill=MOUTH_DARK)
        draw.line(m_poly + [(head_cx - mo_w, mouth_cy)], fill=OUTLINE, width=OUTLINE_W, joint="curve")

        t_w = int(12 * S)
        t_len = int((14 + tongue_ext * 14) * S)
        t_top_y = mouth_cy + int(6 * S)
        tongue_pts = sample_curve([(head_cx - t_w, t_top_y), (head_cx - t_w - int(2*S), t_top_y + t_len), (head_cx, t_top_y + t_len + int(6*S))], 10) + \
                     sample_curve([(head_cx, t_top_y + t_len + int(6*S)), (head_cx + t_w + int(2*S), t_top_y + t_len), (head_cx + t_w, t_top_y)], 10)
        draw.polygon(tongue_pts, fill=TONGUE)
        draw.line(tongue_pts + [tongue_pts[0]], fill=OUTLINE, width=THIN_W, joint="curve")
        draw.line([head_cx, t_top_y + int(2*S), head_cx, t_top_y + t_len + int(2*S)], fill=TONGUE_SHADOW, width=THIN_W)
    else:
        draw.line([head_cx, nose_cy + nose_h - int(1*S), head_cx, mouth_cy + int(2*S)], fill=OUTLINE, width=OUTLINE_W)
        l_smile = sample_curve([(head_cx - int(16*S), mouth_cy - int(3*S)), (head_cx - int(8*S), mouth_cy + int(7*S)), (head_cx, mouth_cy + int(2*S))], 12)
        draw.line(l_smile, fill=OUTLINE, width=OUTLINE_W, joint="curve")
        r_smile = sample_curve([(head_cx, mouth_cy + int(2*S)), (head_cx + int(8*S), mouth_cy + int(7*S)), (head_cx + int(16*S), mouth_cy - int(3*S))], 12)
        draw.line(r_smile, fill=OUTLINE, width=OUTLINE_W, joint="curve")

    # 14. Cheeks Blush
    if blush:
        b_w = int(14 * S)
        b_h = int(8 * S)
        draw.ellipse([head_cx - int(40*S) - b_w, head_cy + int(12*S) - b_h, head_cx - int(40*S) + b_w, head_cy + int(12*S) + b_h], fill=BLUSH)
        draw.ellipse([head_cx + int(40*S) - b_w, head_cy + int(12*S) - b_h, head_cx + int(40*S) + b_w, head_cy + int(12*S) + b_h], fill=BLUSH)

    # 15. Eyebrows
    brow_y = head_cy - int(28 * S)
    brow_w = int(8 * S)
    brow_h = int(5 * S)
    draw.ellipse([head_cx - int(28*S) - brow_w, brow_y - brow_h, head_cx - int(28*S) + brow_w, brow_y + brow_h], fill=COAT_DARK)
    draw.ellipse([head_cx + int(28*S) - brow_w, brow_y - brow_h, head_cx + int(28*S) + brow_w, brow_y + brow_h], fill=COAT_DARK)

    # 16. Eyes
    eye_y = head_cy - int(10 * S)
    for side in (-1, 1):
        eye_cx = head_cx + side * int(27 * S)
        if eye_state == "closed":
            arc_pts = sample_curve([(eye_cx - int(13*S), eye_y + int(2*S)), (eye_cx, eye_y - int(7*S)), (eye_cx + int(13*S), eye_y + int(2*S))], 12)
            draw.line(arc_pts, fill=OUTLINE, width=OUTLINE_W, joint="curve")
        elif eye_state == "happy":
            arc_pts = sample_curve([(eye_cx - int(14*S), eye_y + int(4*S)), (eye_cx, eye_y - int(8*S)), (eye_cx + int(14*S), eye_y + int(4*S))], 14)
            draw.line(arc_pts, fill=OUTLINE, width=int(5*S), joint="curve")
            draw.line([eye_cx + side * int(12*S), eye_y - int(2*S), eye_cx + side * int(17*S), eye_y - int(6*S)], fill=OUTLINE, width=THIN_W)
        elif eye_state == "half":
            ew = int(13 * S)
            eh = int(7 * S)
            draw.ellipse([eye_cx - ew, eye_y - eh + int(3*S), eye_cx + ew, eye_y + eh + int(3*S)], fill=EYE_DARK, outline=OUTLINE, width=THIN_W)
            draw.ellipse([eye_cx - int(4*S), eye_y, eye_cx, eye_y + int(4*S)], fill=(255, 255, 255, 240))
            draw.line([eye_cx - ew - int(2*S), eye_y - int(1*S), eye_cx + ew + int(2*S), eye_y - int(1*S)], fill=OUTLINE, width=OUTLINE_W)
        else: # "open"
            ew = int(14 * S)
            eh = int(16 * S)
            draw.ellipse([eye_cx - ew, eye_y - eh, eye_cx + ew, eye_y + eh], fill=EYE_DARK, outline=OUTLINE, width=THIN_W)
            draw.chord([eye_cx - ew + int(2*S), eye_y - eh + int(10*S), eye_cx + ew - int(2*S), eye_y + eh - int(1*S)], start=0, end=180, fill=EYE_IRIS)
            draw.ellipse([eye_cx - int(8*S), eye_y - int(10*S), eye_cx - int(1*S), eye_y - int(2*S)], fill=(255, 255, 255, 255))
            draw.ellipse([eye_cx + int(2*S), eye_y + int(3*S), eye_cx + int(6*S), eye_y + int(7*S)], fill=(255, 255, 255, 220))

    # 17. Sparkles
    if sparkle:
        for sp_x, sp_y, sp_r in [(head_cx + int(52*S), head_cy - int(32*S), 9), (head_cx - int(54*S), head_cy - int(20*S), 6)]:
            draw.line([sp_x - int(sp_r*S), sp_y, sp_x + int(sp_r*S), sp_y], fill=(255, 215, 0, 240), width=THIN_W)
            draw.line([sp_x, sp_y - int(sp_r*S), sp_x, sp_y + int(sp_r*S)], fill=(255, 215, 0, 240), width=THIN_W)
            draw.ellipse([sp_x - int(2*S), sp_y - int(2*S), sp_x + int(2*S), sp_y + int(2*S)], fill=(255, 255, 255, 255))

    final_img = img.resize((width, height), Image.Resampling.LANCZOS)
    return final_img
