// Buddy the 2D Desktop Overlay Pet - Interactive Preview Engine

const MANIFEST_DATA = {
  character: "Buddy the Cartoon Desktop Dog",
  frame_width: 320,
  frame_height: 320,
  total_frames: 34,
  sequences: {
    idle: {
      title: "Idle Breathing",
      description: "Gentle rhythmic chest expansion, subtle head bobbing, and relaxed tail sway",
      frame_count: 8,
      default_fps: 8,
      loop: true,
      files: [
        "frames/idle/idle_0.png",
        "frames/idle/idle_1.png",
        "frames/idle/idle_2.png",
        "frames/idle/idle_3.png",
        "frames/idle/idle_4.png",
        "frames/idle/idle_5.png",
        "frames/idle/idle_6.png",
        "frames/idle/idle_7.png"
      ],
      spritesheet: "spritesheets/idle_sheet.png",
      row_index: 0
    },
    tail_wag: {
      title: "Tail Wagging",
      description: "Energetic sinusoidal tail wagging with natural hip weight transfer and alert ears",
      frame_count: 8,
      default_fps: 12,
      loop: true,
      files: [
        "frames/tail_wag/tail_wag_0.png",
        "frames/tail_wag/tail_wag_1.png",
        "frames/tail_wag/tail_wag_2.png",
        "frames/tail_wag/tail_wag_3.png",
        "frames/tail_wag/tail_wag_4.png",
        "frames/tail_wag/tail_wag_5.png",
        "frames/tail_wag/tail_wag_6.png",
        "frames/tail_wag/tail_wag_7.png"
      ],
      spritesheet: "spritesheets/tail_wag_sheet.png",
      row_index: 1
    },
    blinking: {
      title: "Blinking",
      description: "Natural eye blink cycle with eyelid squash and subtle head relaxation",
      frame_count: 4,
      default_fps: 6,
      loop: true,
      files: [
        "frames/blinking/blinking_0.png",
        "frames/blinking/blinking_1.png",
        "frames/blinking/blinking_2.png",
        "frames/blinking/blinking_3.png"
      ],
      spritesheet: "spritesheets/blinking_sheet.png",
      row_index: 2
    },
    jumping: {
      title: "Jumping",
      description: "Full Disney-style cartoon jump cycle with anticipation crouch, squash and stretch, airborne apex, and impact compression",
      frame_count: 8,
      default_fps: 10,
      loop: true,
      files: [
        "frames/jumping/jumping_0.png",
        "frames/jumping/jumping_1.png",
        "frames/jumping/jumping_2.png",
        "frames/jumping/jumping_3.png",
        "frames/jumping/jumping_4.png",
        "frames/jumping/jumping_5.png",
        "frames/jumping/jumping_6.png",
        "frames/jumping/jumping_7.png"
      ],
      spritesheet: "spritesheets/jumping_sheet.png",
      row_index: 3
    },
    happy: {
      title: "Happy Expression",
      description: "Joyful reaction with smiling panting tongue, cute squinting eyes, rosy blush, and sparkling stars",
      frame_count: 6,
      default_fps: 8,
      loop: true,
      files: [
        "frames/happy/happy_0.png",
        "frames/happy/happy_1.png",
        "frames/happy/happy_2.png",
        "frames/happy/happy_3.png",
        "frames/happy/happy_4.png",
        "frames/happy/happy_5.png"
      ],
      spritesheet: "spritesheets/happy_sheet.png",
      row_index: 4
    }
  }
};

class PetAnimationApp {
  constructor() {
    this.currentSeqKey = "idle";
    this.currentFrameIdx = 0;
    this.isPlaying = true;
    this.isLooping = true;
    this.fps = 8;
    this.zoom = 1.0;
    this.showGuides = false;
    this.showOnionSkin = false;

    // Cache preloaded Image objects
    this.imageCache = {};
    this.imagesLoaded = 0;
    this.totalImages = 34;

    // Timing
    this.lastFrameTime = 0;
    this.animFrameReq = null;

    // DOM Elements
    this.mainCanvas = document.getElementById("main-canvas");
    this.mainCtx = this.mainCanvas.getContext("2d");
    this.guidesCanvas = document.getElementById("guides-canvas");
    this.guidesCtx = this.guidesCanvas.getContext("2d");
    this.petCanvas = document.getElementById("pet-overlay-canvas");
    this.petCtx = this.petCanvas.getContext("2d");

    this.init();
  }

  async init() {
    this.preloadAllFrames();
    this.setupEventListeners();
    this.renderSequenceList();
    this.renderFilmstrip();
    this.updateControlsUI();
    this.initDesktopPet();
    this.initCodeSnippets();
    this.startLoop();
  }

  preloadAllFrames() {
    for (const [seqKey, seq] of Object.entries(MANIFEST_DATA.sequences)) {
      this.imageCache[seqKey] = [];
      seq.files.forEach((filePath, idx) => {
        const img = new Image();
        img.src = filePath;
        img.onload = () => {
          this.imagesLoaded++;
          if (this.imagesLoaded === 1) {
            this.drawFrame();
          }
        };
        this.imageCache[seqKey].push(img);
      });
    }
  }

  startLoop() {
    const loop = (timestamp) => {
      if (!this.lastFrameTime) this.lastFrameTime = timestamp;
      const interval = 1000 / this.fps;
      const elapsed = timestamp - this.lastFrameTime;

      if (this.isPlaying && elapsed >= interval) {
        this.stepFrame(1);
        this.lastFrameTime = timestamp - (elapsed % interval);
      }

      this.animFrameReq = requestAnimationFrame(loop);
    };
    this.animFrameReq = requestAnimationFrame(loop);
  }

  setSequence(seqKey, autoPlay = true) {
    if (!MANIFEST_DATA.sequences[seqKey]) return;
    this.currentSeqKey = seqKey;
    this.currentFrameIdx = 0;
    const seq = MANIFEST_DATA.sequences[seqKey];
    this.fps = seq.default_fps;
    this.isLooping = seq.loop;

    this.renderSequenceList();
    this.renderFilmstrip();
    this.updateControlsUI();
    this.drawFrame();
    if (autoPlay) this.isPlaying = true;
    this.updatePlayPauseBtn();
  }

  stepFrame(delta) {
    const seq = MANIFEST_DATA.sequences[this.currentSeqKey];
    const total = seq.frame_count;

    if (delta > 0) {
      if (this.currentFrameIdx + 1 < total) {
        this.currentFrameIdx++;
      } else if (this.isLooping) {
        this.currentFrameIdx = 0;
      } else {
        this.isPlaying = false;
        this.updatePlayPauseBtn();
      }
    } else if (delta < 0) {
      if (this.currentFrameIdx - 1 >= 0) {
        this.currentFrameIdx--;
      } else if (this.isLooping) {
        this.currentFrameIdx = total - 1;
      }
    }

    this.drawFrame();
    this.updateTimelineUI();
    this.highlightActiveFilmFrame();
    this.updateSpriteSheetHighlight();
  }

  drawFrame() {
    const frames = this.imageCache[this.currentSeqKey];
    if (!frames || !frames[this.currentFrameIdx]) return;

    const img = frames[this.currentFrameIdx];
    this.mainCtx.clearRect(0, 0, 320, 320);

    // 1. Onion Skinning (Ghost of previous frame)
    if (this.showOnionSkin) {
      const prevIdx = (this.currentFrameIdx - 1 + frames.length) % frames.length;
      const prevImg = frames[prevIdx];
      if (prevImg && prevImg.complete) {
        this.mainCtx.save();
        this.mainCtx.globalAlpha = 0.28;
        this.mainCtx.drawImage(prevImg, 0, 0, 320, 320);
        this.mainCtx.restore();
      }
    }

    // 2. Main Frame
    if (img.complete) {
      this.mainCtx.drawImage(img, 0, 0, 320, 320);
    }

    // 3. Desktop Pet Overlay Canvas sync
    if (this.petCtx && img.complete) {
      this.petCtx.clearRect(0, 0, 320, 320);
      this.petCtx.drawImage(img, 0, 0, 320, 320);
    }

    // 4. Alignment Guides
    this.drawGuides();
  }

  drawGuides() {
    this.guidesCtx.clearRect(0, 0, 320, 320);
    if (!this.showGuides) return;

    this.guidesCtx.save();
    // Center Axis Crosshairs
    this.guidesCtx.strokeStyle = "rgba(59, 130, 246, 0.55)";
    this.guidesCtx.lineWidth = 1;
    this.guidesCtx.setLineDash([4, 4]);

    // Vertical Center (X = 160)
    this.guidesCtx.beginPath();
    this.guidesCtx.moveTo(160, 0);
    this.guidesCtx.lineTo(160, 320);
    this.guidesCtx.stroke();

    // Horizontal Center (Y = 160)
    this.guidesCtx.beginPath();
    this.guidesCtx.moveTo(0, 160);
    this.guidesCtx.lineTo(320, 160);
    this.guidesCtx.stroke();

    // Ground Baseline Contact Plane (Y = 265)
    this.guidesCtx.strokeStyle = "rgba(239, 68, 68, 0.85)";
    this.guidesCtx.lineWidth = 1.5;
    this.guidesCtx.setLineDash([6, 3]);
    this.guidesCtx.beginPath();
    this.guidesCtx.moveTo(20, 265);
    this.guidesCtx.lineTo(300, 265);
    this.guidesCtx.stroke();

    // Ground Baseline Label
    this.guidesCtx.fillStyle = "#ef4444";
    this.guidesCtx.font = "10px JetBrains Mono, monospace";
    this.guidesCtx.fillText("Ground Baseline (Y: 265)", 24, 260);

    // Bounding Box
    this.guidesCtx.strokeStyle = "rgba(245, 158, 11, 0.4)";
    this.guidesCtx.setLineDash([2, 2]);
    this.guidesCtx.strokeRect(40, 40, 240, 240);

    this.guidesCtx.restore();
  }

  updateTimelineUI() {
    const seq = MANIFEST_DATA.sequences[this.currentSeqKey];
    const total = seq.frame_count;
    const progress = (this.currentFrameIdx / (total - 1 || 1)) * 100;

    document.getElementById("scrubber-progress").style.width = `${progress}%`;
    document.getElementById("scrubber-thumb").style.left = `${progress}%`;

    // Indicators
    document.getElementById("live-anim-name").textContent = seq.title;
    document.getElementById("live-frame-indicator").textContent = `Frame ${this.currentFrameIdx + 1} / ${total}`;
    document.getElementById("live-fps-indicator").textContent = `${this.fps} FPS`;
  }

  updateControlsUI() {
    document.getElementById("fps-slider").value = this.fps;
    document.getElementById("fps-display").textContent = `${this.fps} FPS`;
    const ms = Math.round(1000 / this.fps);
    document.getElementById("fps-ms").textContent = `(${ms} ms/frame)`;

    // Update active preset button
    document.querySelectorAll(".fps-preset-btn").forEach(btn => {
      btn.classList.toggle("active", parseInt(btn.dataset.fps) === this.fps);
    });

    // Update scrubber tick marks
    const seq = MANIFEST_DATA.sequences[this.currentSeqKey];
    const ticksContainer = document.getElementById("scrubber-ticks");
    ticksContainer.innerHTML = "";
    for (let i = 0; i < seq.frame_count; i++) {
      const dot = document.createElement("div");
      dot.className = "scrubber-dot";
      dot.style.position = "absolute";
      dot.style.left = `${(i / (seq.frame_count - 1 || 1)) * 100}%`;
      dot.style.top = "50%";
      dot.style.transform = "translate(-50%, -50%)";
      dot.style.width = "4px";
      dot.style.height = "4px";
      dot.style.borderRadius = "50%";
      dot.style.background = "rgba(255, 255, 255, 0.3)";
      ticksContainer.appendChild(dot);
    }

    this.updateTimelineUI();
    this.updateSpriteSheetHighlight();
  }

  updatePlayPauseBtn() {
    const btn = document.getElementById("btn-play-pause");
    if (this.isPlaying) {
      btn.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>`;
      btn.title = "Pause (Spacebar)";
    } else {
      btn.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>`;
      btn.title = "Play (Spacebar)";
    }
  }

  renderSequenceList() {
    const container = document.getElementById("sequence-list");
    container.innerHTML = "";

    const icons = {
      idle: "🫁",
      tail_wag: "🐕",
      blinking: "👀",
      jumping: "🚀",
      happy: "✨"
    };

    for (const [key, seq] of Object.entries(MANIFEST_DATA.sequences)) {
      const item = document.createElement("div");
      item.className = `seq-item ${key === this.currentSeqKey ? "active" : ""}`;
      item.innerHTML = `
        <div class="seq-item-left">
          <span class="seq-icon">${icons[key] || "🐾"}</span>
          <div class="seq-info">
            <h4>${seq.title}</h4>
            <p>${seq.description.slice(0, 48)}...</p>
          </div>
        </div>
        <span class="seq-badge">${seq.frame_count}f</span>
      `;
      item.onclick = () => this.setSequence(key);
      container.appendChild(item);
    }
  }

  renderFilmstrip() {
    const track = document.getElementById("filmstrip-track");
    track.innerHTML = "";
    const seq = MANIFEST_DATA.sequences[this.currentSeqKey];

    seq.files.forEach((filePath, idx) => {
      const frameEl = document.createElement("div");
      frameEl.className = `film-frame ${idx === this.currentFrameIdx ? "active" : ""}`;
      frameEl.id = `film-frame-${idx}`;
      frameEl.innerHTML = `
        <img src="${filePath}" alt="Frame ${idx}">
        <span class="film-frame-label">#${idx}</span>
      `;
      frameEl.onclick = () => {
        this.currentFrameIdx = idx;
        this.isPlaying = false;
        this.updatePlayPauseBtn();
        this.drawFrame();
        this.updateTimelineUI();
        this.highlightActiveFilmFrame();
        this.updateSpriteSheetHighlight();
      };
      track.appendChild(frameEl);
    });
  }

  highlightActiveFilmFrame() {
    document.querySelectorAll(".film-frame").forEach((el, idx) => {
      el.classList.toggle("active", idx === this.currentFrameIdx);
    });
  }

  updateSpriteSheetHighlight() {
    const highlight = document.getElementById("sheet-highlight");
    const img = document.getElementById("sheet-img");
    if (!highlight || !img) return;

    const seq = MANIFEST_DATA.sequences[this.currentSeqKey];
    const row = seq.row_index;
    const col = this.currentFrameIdx;

    // Master sheet has 8 columns and 5 rows
    const scaleX = img.clientWidth / 2560;
    const scaleY = img.clientHeight / 1600;

    const boxW = 320 * scaleX;
    const boxH = 320 * scaleY;
    const boxX = col * 320 * scaleX;
    const boxY = row * 320 * scaleY;

    highlight.style.width = `${boxW}px`;
    highlight.style.height = `${boxH}px`;
    highlight.style.left = `${boxX}px`;
    highlight.style.top = `${boxY}px`;
  }

  setupEventListeners() {
    // Nav Tabs
    document.querySelectorAll(".nav-tab").forEach(tab => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
        tab.classList.add("active");
        const target = document.getElementById(`tab-${tab.dataset.tab}`);
        if (target) target.classList.add("active");
        if (tab.dataset.tab === "spritesheet") {
          setTimeout(() => this.updateSpriteSheetHighlight(), 100);
        }
      });
    });

    // Transport buttons
    document.getElementById("btn-play-pause").onclick = () => {
      this.isPlaying = !this.isPlaying;
      this.updatePlayPauseBtn();
    };

    document.getElementById("btn-prev").onclick = () => {
      this.isPlaying = false;
      this.updatePlayPauseBtn();
      this.stepFrame(-1);
    };

    document.getElementById("btn-next").onclick = () => {
      this.isPlaying = false;
      this.updatePlayPauseBtn();
      this.stepFrame(1);
    };

    const loopBtn = document.getElementById("btn-loop");
    loopBtn.onclick = () => {
      this.isLooping = !this.isLooping;
      loopBtn.classList.toggle("active", this.isLooping);
    };

    // FPS slider & presets
    const fpsSlider = document.getElementById("fps-slider");
    fpsSlider.oninput = (e) => {
      this.fps = parseInt(e.target.value);
      this.updateControlsUI();
    };

    document.querySelectorAll(".fps-preset-btn").forEach(btn => {
      btn.onclick = () => {
        this.fps = parseInt(btn.dataset.fps);
        this.updateControlsUI();
      };
    });

    // Timeline Scrubber Click & Drag
    const scrubberTrack = document.getElementById("scrubber-track");
    let isDraggingScrubber = false;

    const handleScrub = (e) => {
      const rect = scrubberTrack.getBoundingClientRect();
      const clickX = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
      const ratio = clickX / rect.width;
      const seq = MANIFEST_DATA.sequences[this.currentSeqKey];
      this.currentFrameIdx = Math.round(ratio * (seq.frame_count - 1));
      this.drawFrame();
      this.updateTimelineUI();
      this.highlightActiveFilmFrame();
      this.updateSpriteSheetHighlight();
    };

    scrubberTrack.addEventListener("mousedown", (e) => {
      isDraggingScrubber = true;
      this.isPlaying = false;
      this.updatePlayPauseBtn();
      handleScrub(e);
    });

    window.addEventListener("mousemove", (e) => {
      if (isDraggingScrubber) handleScrub(e);
    });

    window.addEventListener("mouseup", () => {
      isDraggingScrubber = false;
    });

    // Background selector buttons
    document.querySelectorAll("[data-bg]").forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll("[data-bg]").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const stage = document.getElementById("stage-container");
        stage.className = `canvas-stage ${btn.dataset.bg}`;
      };
    });

    // Guides & Onion Skinning toggles
    const guidesBtn = document.getElementById("btn-toggle-guides");
    guidesBtn.onclick = () => {
      this.showGuides = !this.showGuides;
      guidesBtn.classList.toggle("active", this.showGuides);
      this.drawGuides();
    };

    const onionBtn = document.getElementById("btn-toggle-onion");
    onionBtn.onclick = () => {
      this.showOnionSkin = !this.showOnionSkin;
      onionBtn.classList.toggle("active", this.showOnionSkin);
      this.drawFrame();
    };

    // Zoom controls
    const canvasWrapper = document.getElementById("canvas-wrapper");
    const zoomText = document.getElementById("zoom-text");

    const updateZoom = (val) => {
      this.zoom = Math.max(0.5, Math.min(2.5, val));
      canvasWrapper.style.transform = `scale(${this.zoom})`;
      zoomText.textContent = `${Math.round(this.zoom * 100)}%`;
    };

    document.getElementById("btn-zoom-in").onclick = () => updateZoom(this.zoom + 0.25);
    document.getElementById("btn-zoom-out").onclick = () => updateZoom(this.zoom - 0.25);
    document.getElementById("btn-zoom-reset").onclick = () => updateZoom(1.0);

    // Interactive Pet Buttons
    document.getElementById("action-pet").onclick = () => {
      this.triggerPetAction("happy", "Awww, puppy love! ❤️");
    };

    document.getElementById("action-jump").onclick = () => {
      this.triggerPetAction("jumping", "Boing! 🚀");
    };

    document.getElementById("action-wag").onclick = () => {
      this.triggerPetAction("tail_wag", "Wag wag wag! 🐕");
    };

    // Global Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;

      if (e.code === "Space") {
        e.preventDefault();
        this.isPlaying = !this.isPlaying;
        this.updatePlayPauseBtn();
      } else if (e.code === "ArrowLeft") {
        e.preventDefault();
        this.isPlaying = false;
        this.updatePlayPauseBtn();
        this.stepFrame(-1);
      } else if (e.code === "ArrowRight") {
        e.preventDefault();
        this.isPlaying = false;
        this.updatePlayPauseBtn();
        this.stepFrame(1);
      } else if (e.code === "Digit1") this.setSequence("idle");
      else if (e.code === "Digit2") this.setSequence("tail_wag");
      else if (e.code === "Digit3") this.setSequence("blinking");
      else if (e.code === "Digit4") this.setSequence("jumping");
      else if (e.code === "Digit5") this.setSequence("happy");
    });

    // Resize event for sprite sheet highlight
    window.addEventListener("resize", () => {
      this.updateSpriteSheetHighlight();
    });
  }

  triggerPetAction(seqKey, speechText) {
    this.setSequence(seqKey);
    const bubble = document.getElementById("pet-bubble");
    if (bubble) {
      bubble.textContent = speechText;
      bubble.classList.add("show");
      setTimeout(() => bubble.classList.remove("show"), 2200);
    }
  }

  initDesktopPet() {
    const petEl = document.getElementById("draggable-pet");
    const screenEl = document.getElementById("desktop-screen");
    if (!petEl || !screenEl) return;

    let isDragging = false;
    let startX = 0;
    let startY = 0;
    let initialLeft = 0;
    let initialTop = 0;

    petEl.addEventListener("mousedown", (e) => {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      initialLeft = petEl.offsetLeft;
      initialTop = petEl.offsetTop;
      e.preventDefault();
    });

    window.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;

      const maxLeft = screenEl.clientWidth - petEl.clientWidth;
      const maxTop = screenEl.clientHeight - petEl.clientHeight - 42; // Above taskbar

      const newLeft = Math.max(0, Math.min(initialLeft + dx, maxLeft));
      const newTop = Math.max(0, Math.min(initialTop + dy, maxTop));

      petEl.style.left = `${newLeft}px`;
      petEl.style.top = `${newTop}px`;
    });

    window.addEventListener("mouseup", () => {
      isDragging = false;
    });

    // Pet click interactions
    petEl.addEventListener("click", () => {
      // Toggle jump or happy reaction
      if (this.currentSeqKey === "idle") {
        this.triggerPetAction("jumping", "Yippee! 🐾");
      } else {
        this.triggerPetAction("happy", "Hehe, tickles! 💕");
      }
    });

    // Scale selector
    const scaleSelect = document.getElementById("sim-scale-select");
    scaleSelect.onchange = (e) => {
      const scale = parseFloat(e.target.value);
      const canvas = document.getElementById("pet-overlay-canvas");
      canvas.style.width = `${320 * scale}px`;
      canvas.style.height = `${320 * scale}px`;
    };

    // Reset pet position
    document.getElementById("btn-reset-pet-pos").onclick = () => {
      petEl.style.left = "65%";
      petEl.style.top = "48%";
    };

    // Clock in taskbar
    const updateClock = () => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const clockEl = document.getElementById("taskbar-clock");
      if (clockEl) clockEl.textContent = timeStr;
    };
    updateClock();
    setInterval(updateClock, 30000);
  }

  initCodeSnippets() {
    const snippets = {
      html: `<!-- HTML5 Canvas Animation Player for Desktop Overlay -->
<canvas id="dogOverlay" width="320" height="320"></canvas>

<script>
const canvas = document.getElementById('dogOverlay');
const ctx = canvas.getContext('2d');
const spriteSheet = new Image();
spriteSheet.src = 'spritesheet.png';

// Row 0: Idle (8 frames), Row 1: Tail Wag (8f), Row 2: Blink (4f), Row 3: Jump (8f), Row 4: Happy (6f)
let currentFrame = 0;
const totalFrames = 8;
const row = 0; // Idle
const fps = 8;

setInterval(() => {
  ctx.clearRect(0, 0, 320, 320);
  ctx.drawImage(
    spriteSheet,
    currentFrame * 320, row * 320, 320, 320, // Source rect
    0, 0, 320, 320                           // Dest rect
  );
  currentFrame = (currentFrame + 1) % totalFrames;
}, 1000 / fps);
<\/script>`,

      css: `/* CSS Keyframe Sprite Sheet Animation */
.dog-character {
  width: 320px;
  height: 320px;
  background-image: url('spritesheets/idle_sheet.png');
  background-repeat: no-repeat;
  animation: dog-idle 1.0s steps(8) infinite;
}

@keyframes dog-idle {
  from { background-position: 0 0; }
  to { background-position: -2560px 0; }
}

/* Tail Wagging Sequence */
.dog-character.wag {
  background-image: url('spritesheets/tail_wag_sheet.png');
  animation: dog-wag 0.67s steps(8) infinite;
}

@keyframes dog-wag {
  from { background-position: 0 0; }
  to { background-position: -2560px 0; }
}`,

      flutter: `// Flutter Transparent Desktop Overlay Window
import 'package:flutter/material.dart';

class DesktopDogOverlay extends StatefulWidget {
  const DesktopDogOverlay({Key? key}) : super(key: key);

  @override
  State<DesktopDogOverlay> createState() => _DesktopDogOverlayState();
}

class _DesktopDogOverlayState extends State<DesktopDogOverlay>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  int _frame = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..addListener(() {
        setState(() {
          _frame = (_controller.value * 8).floor() % 8;
        });
      })..repeat();
  }

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      'assets/frames/idle/idle_\$_frame.png',
      width: 240,
      height: 240,
    );
  }
}`,

      electron: `// Electron Transparent Click-Through Overlay Window (main.js)
const { app, BrowserWindow } = require('electron');

app.whenReady().then(() => {
  const overlayWindow = new BrowserWindow({
    width: 320,
    height: 320,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    hasShadow: false,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: true,
    }
  });

  // Enable dragging / positioning anywhere on desktop screen
  overlayWindow.setIgnoreMouseEvents(false);
  overlayWindow.loadFile('index.html');
});`
    };

    const codeDisplay = document.getElementById("code-display");
    const codeTabs = document.querySelectorAll(".code-tab");

    codeTabs.forEach(tab => {
      tab.addEventListener("click", () => {
        codeTabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        const type = tab.dataset.code;
        codeDisplay.textContent = snippets[type] || "// Code snippet not found";
      });
    });

    // Default snippet
    if (codeDisplay) codeDisplay.textContent = snippets["html"];
  }
}

// Instantiate once DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.petApp = new PetAnimationApp();
});
