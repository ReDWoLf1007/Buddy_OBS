# Buddy — 2D Animated Cartoon Dog Overlay

A complete, production-grade 2D animated cartoon character designed specifically for desktop overlays, game engines, and companion apps.

---

## 🎨 Character Specifications

- **Character Name:** Buddy the Cartoon Dog
- **Breed / Aesthetic:** Golden Retriever / Corgi cartoon hybrid with warm golden amber coat, floppy caramel ears, creamy muzzle and chest patch, cherry red collar with a shiny golden bell tag, expressive glossy eyes, and a joyful wagging tail.
- **Dimensions:** Exactly **320 × 320 px** per frame across all sequences.
- **Color Depth & Alpha:** 32-bit RGBA with **100% transparent backgrounds** (clean alpha channels, no edge halos).
- **Proportion Consistency:** Vector-based procedural rendering with 4x supersampling (1280x1280 downsampled via Lanczos filtering) guaranteeing mathematically identical proportions, line weights (4.5px outline), palettes, and ground anchor alignment across every frame.
- **Total Frames:** **34 frames** across 5 distinct animation cycles.

---

## 🎬 Animation Sequences Breakdown

| Sequence | Frames | Default FPS | Duration | Animation Characteristics & Physics |
| :--- | :---: | :---: | :---: | :--- |
| **1. Idle Breathing** | 8 | 8 FPS | 1.00 s | Smooth sine-wave chest expansion/rise, subtle head bob (2.5px), gentle tail sway, relaxed compliant ears. Loops seamlessly. |
| **2. Tail Wagging** | 8 | 12 FPS | 0.67 s | Sinusoidal wag arc between &plusmn;28&deg;, dynamic hip weight shifting in opposite phase for realistic balance, alert perked ears. Loops seamlessly. |
| **3. Blinking** | 4 | 6 FPS | 0.67 s | Natural eyelid squash cycle: Open &rarr; Half-blink &rarr; Fully closed curved lash line &rarr; Half-open recovery &rarr; Open. |
| **4. Jumping** | 8 | 10 FPS | 0.80 s | Full Disney 12-principles cartoon jump: Anticipation crouch (-14px squash), takeoff stretch, 50px peak height with tucked paws and joyful pant, falling descent, ground touchdown, landing impact squash, and rebound. |
| **5. Happy Expression** | 6 | 8 FPS | 0.75 s | Joyful reaction: mouth opens into a broad smile, cute pink tongue pops out panting, eyes squint into happy `^ ^` arcs, rosy cheeks blush, and golden sparkle star glints twinkle. |

---

## 📁 Directory Structure

```text
desktop_pet_dog/
├── index.html                  # Interactive HTML5/CSS/JS preview application
├── style.css                   # Glassmorphism dark-theme styling & responsive layout
├── app.js                      # Playback engine, FPS adjuster, timeline scrubber, overlay simulator
├── spritesheet.png             # Master Sprite Sheet Atlas (2560 × 1600 px)
├── spritesheet.json            # Machine-readable JSON Atlas with exact frame rects
├── dog_generator.py            # Parametric vector rendering engine (Pillow)
├── generate_assets.py          # Frame batch generator & sprite sheet compiler
├── verify.py                   # Automated asset validation script
├── spritesheets/               # Individual sequence horizontal sprite sheets
│   ├── idle_sheet.png          # 8 frames (2560 × 320 px)
│   ├── tail_wag_sheet.png      # 8 frames (2560 × 320 px)
│   ├── blinking_sheet.png      # 4 frames (1280 × 320 px)
│   ├── jumping_sheet.png       # 8 frames (2560 × 320 px)
│   └── happy_sheet.png         # 6 frames (1920 × 320 px)
└── frames/                     # Individual 320x320 PNG frames
    ├── idle/                   # idle_0.png .. idle_7.png
    ├── tail_wag/               # tail_wag_0.png .. tail_wag_7.png
    ├── blinking/               # blinking_0.png .. blinking_3.png
    ├── jumping/                # jumping_0.png .. jumping_7.png
    └── happy/                  # happy_0.png .. happy_5.png
```

---

## 🚀 How to Launch the Preview Application

Simply double-click `index.html` or open it in any web browser:

```bash
# Or run with python local server if preferred:
python -m http.server 8000 --directory desktop_pet_dog
# Then navigate to: http://localhost:8000
```

### Preview App Features:
1. **Interactive Animation Player:**
   - Play, pause, step forward, step backward, loop toggle.
   - FPS slider (1 to 30 FPS) with quick presets (4, 8, 12, 16, 24 FPS) and live millisecond/frame calculation.
   - Clickable interactive timeline scrubber and filmstrip frame selector.
2. **Alignment & Consistency Verification:**
   - **Onion Skinning:** Displays a translucent ghost of the previous frame to visually confirm smooth transitions and anatomical consistency.
   - **Alignment Guides:** Toggleable ground baseline contact plane (Y: 265), center crosshairs, and bounding boxes.
   - **Background Switcher:** Dark Grid, Light Grid, Solid Black, Solid White, Chroma Green, and Desktop Wallpaper.
   - **Zoom Controls:** 50% to 250% zoom.
3. **Sprite Sheet Atlas Inspector:**
   - Real-time animated bounding box overlay tracking the current frame directly on the master sprite sheet.
   - Direct download links for the combined sheet and JSON metadata atlas.
4. **Desktop Overlay Simulator:**
   - Interactive draggable pet widget over a simulated OS desktop.
   - Click to make Buddy jump, pet him to trigger the happy expression, or adjust overlay scale (50%, 75%, 100%).

---

## 💻 Integration Guide

### 1. HTML5 Canvas
```javascript
const canvas = document.getElementById('petOverlay');
const ctx = canvas.getContext('2d');
const spriteSheet = new Image();
spriteSheet.src = 'spritesheet.png';

let frameIndex = 0;
const totalFrames = 8;
const rowIndex = 0; // 0: Idle, 1: Tail Wag, 2: Blink, 3: Jump, 4: Happy
const fps = 8;

setInterval(() => {
  ctx.clearRect(0, 0, 320, 320);
  ctx.drawImage(
    spriteSheet,
    frameIndex * 320, rowIndex * 320, 320, 320,
    0, 0, 320, 320
  );
  frameIndex = (frameIndex + 1) % totalFrames;
}, 1000 / fps);
```

### 2. CSS Sprite Sheet Keyframes
```css
.desktop-dog-idle {
  width: 320px;
  height: 320px;
  background-image: url('spritesheets/idle_sheet.png');
  background-repeat: no-repeat;
  animation: dogIdle 1.0s steps(8) infinite;
}

@keyframes dogIdle {
  from { background-position: 0 0; }
  to { background-position: -2560px 0; }
}
```

### 3. Electron Desktop Overlay (Transparent Window)
```javascript
const { app, BrowserWindow } = require('electron');

app.whenReady().then(() => {
  const win = new BrowserWindow({
    width: 320,
    height: 320,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    hasShadow: false,
    skipTaskbar: true
  });
  win.loadFile('index.html');
});
```

---

## 📺 OBS Studio Streaming Integration

Buddy includes dedicated streaming modules designed specifically for **OBS Studio**, **Streamlabs Desktop**, and **Twitch/YouTube streams**:

### 1. Dedicated OBS Overlay (`obs_overlay.html`)
- **100% Transparent Background**: Tailored for OBS Browser Sources.
- **Organic Random Activity Engine**: In stream mode, Buddy behaves like a real pet—breathing calmly, occasionally blinking, wagging his tail, or doing a playful jump every few seconds.
- **Subscriber Alert Reaction**:
  - Automatically interrupts or transitions to an excited **Jump** followed by a cheerful **Happy Expression** (panting tongue, wagging tail, rosy blush, sparkling star glints).
  - Pops an animated **Cartoon Thought Bubble** with floating cloud dots: `✨ NEW SUBSCRIBER! ✨ Thank you, <subscriber_name>! 🐾💖`.
  - Emits bursting sparkle/heart particle effects.
  - Speaks *"Thank you, <subscriber_name>!"* using the built-in Text-To-Speech (Web Speech API) and plays a cheerful chime (Web Audio API).
  - Handles **Alert Queuing**: If multiple subscribers arrive in quick succession, Buddy greets each in sequence.

### 2. Streamer Control Dock (`obs_dock.html`)
- Can be docked directly into OBS Studio (*Docks &rarr; Custom Browser Docks...*) or kept open on a secondary monitor or tablet.
- Features zero-latency local communication with the overlay via `BroadcastChannel` and `localStorage`.
- Includes instant test buttons, manual animation triggers (*Force Jump*, *Force Wag*, *Custom Thoughts*), TTS toggle, and random behavior frequency controls.

### 3. Quick Setup in OBS Studio
1. Start the included stream server in your project folder:
   ```powershell
   python server.py
   ```
   *(Or standard `python -m http.server 8000`)*
2. **Add Browser Source in OBS**:
   - URL: `http://localhost:8000/obs_overlay.html`
   - Width: `440`, Height: `490`
   - Check *Control audio via OBS* (optional)
   - Uncheck *Shutdown source when not visible*
3. **Add Control Dock in OBS**:
   - In OBS menu: **Docks** &rarr; **Custom Browser Docks...**
   - Dock Name: `Buddy Pet Control`
   - URL: `http://localhost:8000/obs_dock.html`
   - Click *Apply* and dock it next to your chat or mixer!

---

## 🔴 Automatic YouTube & 🟣 Twitch Live Detection

Buddy connects dynamically to live streams to automatically detect real subscriber names without requiring manual clicks:

### How Dynamic Alerts Work:
1. **Zero-Lag Streamlabs Socket API (Recommended for YouTube & Twitch)**:
   - Connect your YouTube channel or Twitch account to [Streamlabs.com](https://streamlabs.com) (free).
   - In Streamlabs, copy your **Socket API Token** (*Settings &rarr; API Settings &rarr; API Tokens*).
   - Paste it into the **Buddy Control Dock** under **Auto-Alerts** and click **Save**.
   - Whenever someone subscribes, becomes a **Channel Member**, or sends a **Super Chat** on YouTube (or subscribes on Twitch), Buddy instantly receives the event, triggers the celebratory jump, wags his tail, displays their real name in the thought bubble, and speaks their name via Text-To-Speech!
2. **AFK & Custom Thought Bubble Mode**:
   - In the Control Dock, switch to the **AFK & Quick Reactions** tab to pop up instant thought bubbles while you're away:
     - ☕ *BRB getting coffee!*
     - ⏱️ *Taking a quick 5 min break!*
     - 🎮 *Stream Starting Soon!*
     - Or any custom text you type!
3. **Direct HTTP Webhook**:
   - You can also trigger alerts from external scripts or bots via:
     `http://localhost:8000/api/alert?name=SubscriberName&platform=youtube&tier=Subscriber`
