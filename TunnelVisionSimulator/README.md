# Glaucoma Visual Field Research Visualizer & Algorithm Comparison Tool
**Department of Computer Science & Engineering, LU**  
**Course:** Computer Graphics Sessional  
**Assignment:** Bridge to the Real World — Design & Build  
**Career Track:** **Track B: Higher Study — MS / PhD Abroad**  
**Suggested Domain:** Algorithm comparison tool, research visualiser  

---

## 📌 Part 1 — Problem Discovery

### 1. Which career track have you chosen?
**Track B: Higher Study — MS / PhD abroad (Research Visualizer & Algorithm Comparison).**  
This track focuses on using Computer Graphics algorithms to model, visualize, and solve scientific and biomedical research problems.

### 2. What is your project idea?
**Glaucoma Visual Field Research Visualizer & Perimetry Screening Tool.**  
Glaucoma is known as the **"Silent Thief of Sight"** because patients lose peripheral vision gradually without pain, while central vision (reading) remains intact. By the time a patient notices, significant irreversible optic nerve damage has occurred. Clinical perimeter machines (like Humphrey Field Analyzers) cost upwards of \$25,000–\$35,000 and are unavailable in remote or low-income areas.  
This tool solves that problem by:
1. Providing an accessible visual field loss visualizer and self-screening tool.
2. Comparing the mathematical **Cohen-Sutherland Line Clipping Algorithm** against biological **Radial Scotoma Masking** as two approaches to modeling visual field constriction.
3. Enabling single-eye testing (**Left Eye [OS]** or **Right Eye [OD]**) as required by clinical ophthalmology research standards.

### 3. Which Computer Graphics concepts does your project use?
The project uses **4 core Computer Graphics techniques**:
1. **Line & Shape Drawing**: Vector primitives (`GL_QUADS`, `GL_POLYGON`, `GL_LINES`) for background, vehicle, traffic light, and perimetry targets.
2. **2D Geometric Transformations**: Scaling transformation to dynamically adjust vision radius using the keyboard (`+` and `-`).
3. **Color Fill**: Tunnel vision peripheral mask rendering using `GL_TRIANGLE_STRIP` to create the opaque scotoma boundary and optic nerve blind spot.
4. **Line Clipping**: The **Cohen-Sutherland Line Clipping Algorithm** implemented from scratch with 4-bit region codes (`INSIDE`, `LEFT`, `RIGHT`, `BOTTOM`, `TOP`) to clip road markings to the visual field boundary.

### 4. Find two real-world systems using similar techniques
1. **Zeiss Humphrey Field Analyzer 3 (HFA3) / Octopus 900**: Standard clinical perimetry instruments used by ophthalmologists worldwide that map visual field scotomas by presenting light stimuli at varying eccentricities while maintaining central fixation.
2. **Melbourne Rapid Fields (MRF) / Eyecatcher**: Tablet-based visual field research visualizers developed for home monitoring and clinical trials to track glaucoma progression without large perimeter hardware.

---

## 💻 Part 2 — Implementation & Code Overview

- **Language:** Python (`PyOpenGL`, `PyOpenGL_accelerate`, `freeglut`)
- **File:** `tunnel_vision_simulator.py` (~280 lines of clean, simple code)
- **Animation:** None (clean static rendering; updates only on user interaction, 0% idle CPU)
- **Storage:** Self-contained in-memory calculation (no extra CSV or external datasets needed)
- **Viewport:** Single clean window (no split screen clutter)

### Controls:
| Key | Action | Research Purpose |
| :---: | :---: | :--- |
| `L` | **Left Eye (OS)** | Shifts physiological blind spot to left temporal field |
| `R` | **Right Eye (OD)** | Shifts physiological blind spot to right temporal field |
| `V` | **Toggle View** | Switches between Normal Vision and Glaucoma Tunnel Vision |
| `+` / `-` | **Scale Radius** | 2D Transformation adjusting visual field size (50px to 280px) |
| `C` | **Toggle Clip Box** | Shows / hides Cohen-Sutherland rectangular bounding box |
| `T` | **Start Test** | Launches interactive 8-point perimetry screening |
| Click | **Record Hit** | Click the stimulus dot to test peripheral perception |
| `Q` / `ESC`| **Exit** | Closes application |

### Mandatory Comment Style Used:
Every core function follows the mandatory 3-line format:
```python
# কী করছে: ...
# কেন লাগছে: ...
# real world-এ এটা কোথায় দেখা যায়: ...
```

---

## 📝 Part 3 — Reflection Report (The Five Questions)

### Q1. Where did you get most stuck?
**Problem:** In the Cohen-Sutherland line clipping algorithm, converting screen coordinates to clip against a dynamically resizing circular field caused visual clipping artifacts when lines crossed corners.  
**Solution:** I derived an exact rectangular bounding window `[xmin, ymin, xmax, ymax]` from the central gaze coordinates `(CENTER_X, CENTER_Y)` and current `vision_radius`, updating the region outcodes bitwise (`code |= LEFT`, `RIGHT`, `BOTTOM`, `TOP`) before recomputing line intersection equations.

### Q2. What did this project teach you that classroom theory could not?
In class, line clipping and color fill are taught as abstract mathematical formulas. Building this project showed me that **line clipping is actually a computer vision model for biological field restriction**. When an eye suffers tunnel vision, the brain stops receiving line segments outside the visual window—which behaves identically to discarding segments using outcode bitwise operations (`code1 & code2 != 0`).

### Q3. How does this connect to your career track (Higher Study — MS/PhD abroad)?
In medical imaging and biomedical visualization research abroad, researchers use computer graphics algorithms to simulate physiological defects (such as low-vision simulators for VR/AR, retinal implants, and autonomous driving hazard awareness for visually impaired pedestrians). This project demonstrates the ability to translate a clinical ophthalmology problem into a working algorithmic prototype.

### Q4. If you had one more week, what would you add?
1. An empirical contrast sensitivity slider (dimming the scene to simulate low-light night-blindness in glaucoma).
2. Arcuate scotoma patterns (curved Bjerrum scotomas) using 2D Bezier curves.

### Q5. Would you recommend this type of project in CG lab?
**Yes, strongly.** Unlike drawing static cartoon houses or flowers, building a "Bridge to the Real World" tool that addresses a real medical condition (glaucoma) gives the code purpose and prepares students for thesis research and graduate school interviews.

---

## 🎤 Part 4 — Viva & Live Modification Preparation

Common questions you can easily defend during your viva:

1. **"Delete this line of code. What happens?"**
   - If you comment out `draw_glaucoma_scotoma()`: The scene displays in full normal vision without any tunnel vision mask.
   - If you comment out `clipped = cohen_sutherland_clip(...)`: The yellow road lane markings will either disappear or remain unclipped.
   - If you comment out `draw_circle(...)` in the car function: The car wheels disappear.

2. **"Walk me through the Cohen-Sutherland function."**
   - Explain: It assigns a 4-bit region code (`INSIDE=0`, `LEFT=1`, `RIGHT=2`, `BOTTOM=4`, `TOP=8`) to both line endpoints. If both are `0000`, the line is trivially accepted. If `code1 & code2 != 0`, both endpoints share an outside region and the line is discarded. Otherwise, it calculates the line intersection with the boundary using slope equations:
     $$x = x_1 + (x_2 - x_1) \cdot \frac{y_{\text{bound}} - y_1}{y_2 - y_1}$$

3. **"Why is only Left or Right eye available at a time?"**
   - In clinical ophthalmology and perimetry research (such as Humphrey Field Analyzer testing), eyes are always tested **monocularly** (one eye covered) because glaucoma progresses asymmetrically. The natural blind spot is on the temporal side (left for Left Eye, right for Right Eye).
