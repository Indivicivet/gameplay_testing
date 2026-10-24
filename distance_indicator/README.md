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

### 2. Consistent 4-Tier Visual Effects & Presets (Image 2)
All 4 distance zones now feature consistent, stepped visual indicators across 4 calibrated tiers:
* **Tier 1 (Alert: 2.5m – 2.0m)**: Sparse corner speed marks (wide aperture 0.40, alpha 0.55, blur 0.25).
* **Tier 2 (Threat: 2.0m – 1.5m)**: Medium radial focus lines (aperture 0.32, alpha 0.75, blur 0.50).
* **Tier 3 (Danger: 1.5m – 1.0m)**: Dense manga action lines (tighter aperture 0.24, alpha 0.90, blur 0.75).
* **Tier 4 (Clinch: < 1.0m)**: Maximum speed storm lines (tight focus aperture 0.16, alpha 1.00, blur 1.00).

Press keys `1` through `5` at runtime to switch styles:
1. **Sprint / Pure Optical Radial Blur (`Key 1`)**:
   - High-quality 16-sample optical radial zoom blur radiating outward towards screen edges.
   - Clean photographic motion blur with zero chromatic aberration / color-fringing.
2. **Manga Action Lines (`Key 2`)**:
   - High-contrast radiating action focus lines matching Image 2 across all 4 tiers.
3. **Combat Tunnel Vignette (`Key 3`)**:
   - Deep peripheral vignette and lens darkening combined with optical blur and corner lines.
4. **White Sprint Rush (`Key 4`)**:
   - White speed lines across all 4 tiers for an alternate high-intensity rush aesthetic.
5. **Full Hybrid (`Key 5`, Default)**:
   - Full synthesis of action lines, optical radial blur, peripheral vignette, and dynamic FoV.

### 3. Inward Field of View Tightening (`ZOOM_CONST`)
Camera FoV tightens dramatically as you get closer, compounding forward motion and physical threat rather than canceling it out:
$$\text{FOV} = \text{BASE\_FOV} + \text{ZOOM\_CONST} \cdot f(d) + \text{Transition Kick} + \text{Breathing}$$
* **Stepped Inward Tightening**: Camera FoV tightens from **72.0°** at safe range down to **48.0°** in the clinch zone ($-24.0^\circ$ total telephoto contraction, $-6.0^\circ$ per tier step):
  - **Safe ($> 2.5\text{m}$)**: $72.0^\circ$ (wide, comfortable view of the arena)
  - **Zone 1: Alert ($2.5\text{m} - 2.0\text{m}$)**: $66.0^\circ$ ($-6.0^\circ$ tighter zoom)
  - **Zone 2: Threat ($2.0\text{m} - 1.5\text{m}$)**: $60.0^\circ$ ($-12.0^\circ$ tighter zoom)
  - **Zone 3: Danger ($1.5\text{m} - 1.0\text{m}$)**: $54.0^\circ$ ($-18.0^\circ$ tighter zoom)
  - **Zone 4: Clinch ($< 1.0\text{m}$)**: $48.0^\circ$ ($-24.0^\circ$ intense tunnel focus)
* **Punchy Inward Snap Kick**: **-5.0°** dynamic inward snap kick upon crossing each distance threshold closer to the opponent.
* **Clinch Breathing**: Subtle ±0.8° breathing cycle when inside the close infighting clinch zone ($d \le 1.0\text{m}$).
* **Live In-Game FoV Tuning**: Press `[` to intensify inward zoom tightening or `]` to soften it (range $-45.0^\circ$ to $+30.0^\circ$).

### 4. High-Contrast Environment & HUD Diagnostics
* **Light Sparring Arena**: Clean, bright floor mat and neutral sky with dark slate pillars, ensuring inky manga speed lines and ground markers pop with maximum visual contrast.
* **Ground Rings & Spoiler Toggle**: Concentric colored floor rings centered beneath the opponent at **2.5m** (Azure Blue Alert), **2.0m** (Amber Gold Threat), **1.5m** (Vivid Orange Danger), and **1.0m** (Crimson Red Clinch).
  - Press `Z` at any time to toggle ground rings on/off so you can test distance perception with or without ground "spoilers".
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
| `Z` | **Toggle Ground Rings On/Off (Distance Spoilers)** |
| `M` | Toggle Opponent AI (`Milling` $\rightarrow$ `Standing Still` $\rightarrow$ `Slow Advance`) |
| `C` | Toggle Camera (`3rd-Person Follow` $\rightarrow$ `Over-The-Shoulder` $\rightarrow$ `1st-Person`) |
| `[` / `]` | Adjust `ZOOM_CONST` (FoV jump strength $\pm 4^\circ$) |
| `R` | Reset player and opponent positions |
