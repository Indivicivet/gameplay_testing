# Distance Indicator Prototype

A 3D third-person prototype testing distance indicators, sharp multi-tier response curves, and motion/focus border effects inspired by fighting games and sprint mechanics.

## Quick Start

Run the game directly with Python:
```bash
python main.py
```
Or double-click `run.bat`.

---

## Features

### 1. Stepped / Bumpy Response Curve $f(d)$ (Image 1)
The distance response curve matches the hand-drawn multi-terrace curve in Image 1 across the **1.0m – 2.5m** center-to-center fighting range:
* **Safe Range ($> 2.5\text{ m}$)**: $f(d) = 0.0$ (Zero FX, clean field of view).
* **Zone 1: Alert ($2.0\text{ m} < d \le 2.5\text{ m}$)**: Sharp jump to the first plateau ($\approx 0.25$).
* **Zone 2: Threat ($1.5\text{ m} < d \le 2.0\text{ m}$)**: Sharp jump to the second plateau ($\approx 0.50$).
* **Zone 3: Danger ($1.0\text{ m} < d \le 1.5\text{ m}$)**: Sharp jump to the third plateau ($\approx 0.75$).
* **Zone 4: Clinch / Infighting ($d \le 1.0\text{ m}$)**: Sharp spike to maximum intensity ($1.00$).

Transitions are smooth yet decisive step jumps. All sudden peripheral white screen flashing has been removed for a clean visual experience. Movement speeds are slowed down (Player: 1.26 m/s, Opponent: 0.63 m/s) for deliberate distance testing.

### 2. Visual Effects & Presets (Image 2)
Press keys `1` through `5` at runtime to test different visual styles:
1. **Sprint / Radial Blur (`Key 1`)**:
   - Radial zoom blur intensifying towards outer screen borders.
   - Dynamic chromatic aberration (RGB channel dispersion).
   - Dynamic FoV dilation.
2. **Manga Action Lines (`Key 2`)**:
   - High-contrast radiating action focus lines matching Image 2.
   - Organic angular jitter and aperture contraction as distance closes.
3. **Combat Tunnel Vignette (`Key 3`)**:
   - Deep peripheral vignette and lens darkening.
   - Edge chromatic aberration.
4. **White Sprint Rush (`Key 4`)**:
   - White speed lines and edge bloom for high-intensity action.
5. **Full Hybrid (`Key 5`, Default)**:
   - Harmonized combination of action lines, radial zoom blur, chromatic aberration, peripheral vignette, and dynamic FoV.

### 3. Light Field of View Modulation (`ZOOM_CONST`)
Camera FoV modulates smoothly as you transition between regions:
$$\text{FOV} = \text{BASE\_FOV} + \text{ZOOM\_CONST} \cdot f(d) + \text{Transition Kick} + \text{Breathing}$$
* **Stepped Widening**: FoV comfortably expands from 62.0° (safe range) to 72.0° (clinch zone), enhancing speed perception and spatial awareness.
* **Transition Kick**: +2.2° dynamic optical kick upon crossing each distance boundary into a closer tier.
* **Clinch Breathing**: Subtle ±0.5° breathing cycle when inside the close infighting clinch zone ($d \le 1.0\text{m}$).
* **Live In-Game FoV Tuning**: Press `[` to decrease or `]` to increase `ZOOM_CONST` (range $-25.0^\circ$ to $+35.0^\circ$). Positive values zoom out as distance decreases; negative values zoom in.

### 4. High-Contrast Environment & HUD Diagnostics
* **Light Sparring Arena**: Clean, bright floor mat and neutral sky with dark slate pillars, ensuring inky manga speed lines and ground markers pop with maximum visual contrast.
* **Ground Rings**: Concentric colored floor rings centered beneath the opponent at **2.5m** (Azure Blue Alert), **2.0m** (Amber Gold Threat), **1.5m** (Vivid Orange Danger), and **1.0m** (Crimson Red Clinch).
* **High-Contrast HUD Cards**: Semi-transparent dark backing cards behind the top Distance banner, bottom-left status readout, and bottom-right controls panel ensure 100% legibility under any lighting or camera angle.
* **Layer Depth Ordering**: Speed lines render behind the HUD, so diagnostic readouts and controls remain crisp and unobstructed.
* **Live Curve Graph**: Renders the Image 1 response curve in the top-right corner with a real-time tracking dot showing current distance $d$ and intensity $f(d)$.
* **Camera Modes**: Toggle with `C` between 3rd-person follow, over-the-shoulder, and 1st-person.
* **Opponent AI**: Toggle with `M` between milling around slowly, standing still (for precise measurement), or following.

---

## Controls Reference

| Key | Action |
| :--- | :--- |
| `W, A, S, D` | Walk around (slow, deliberate testing pace) |
| `Mouse Move` / `Q, E` | Orbit camera (Mouse look or Q/E keys) |
| `Left Click` | Capture mouse cursor |
| `ESC` | Unlock / Lock mouse cursor |
| `1, 2, 3, 4, 5` | Switch FX Preset (Sprint Blur, Manga Lines, Vignette, White Rush, Hybrid) |
| `M` | Toggle Opponent AI (`Milling` $\rightarrow$ `Standing Still` $\rightarrow$ `Slow Advance`) |
| `C` | Toggle Camera (`3rd-Person Follow` $\rightarrow$ `Over-The-Shoulder` $\rightarrow$ `1st-Person`) |
| `[` / `]` | Decrease / Increase `ZOOM_CONST` ($\pm 2^\circ$) |
| `R` | Reset player and opponent positions |
