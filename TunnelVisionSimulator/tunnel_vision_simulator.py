import math 
import random 
from OpenGL.GL import * 
from OpenGL.GLUT import * 
from OpenGL.GLU import * 
 
 
# কী করছে: OpenGL window-এর width ও height নির্ধারণ করছে।
# কখন লাগছে: Window তৈরি এবং coordinate system সেট করার সময়।
# real world-এ এটা কোথায় দেখা যায়: Computer graphics-এর screen/window size নির্ধারণে।
WIDTH, HEIGHT = 600, 650 
 
CENTER_X, CENTER_Y = WIDTH // 2, 330 
vision_radius = 200 
MIN_RADIUS = 50 
MAX_RADIUS = 280 
 
# কী করছে: কোন চোখ বর্তমানে দেখা হচ্ছে তা নির্ধারণ করছে।
# কখন লাগছে: Left/Right eye mode পরিবর্তন ও display করার সময়।
# real world-এ এটা কোথায় দেখা যায়: Eye screening বা visual field test-এ।
current_eye = "RIGHT"         
glaucoma_mode = True         
show_clip_box = True         
 
test_mode = False 
test_finished = False 
test_index = 0 
NUM_TEST_POINTS = 8 
target_point = (0, 0) 
test_results = []           # Stores (x, y, hit_bool) 
HIT_TOLERANCE = 45          # Click tolerance in pixels 
 
 
 
# 2. Line & Shape Drawing (Primitives) 
 
# কী করছে: নির্দিষ্ট center, radius ও color দিয়ে circle আঁকে।
# কখন লাগছে: চাকা, signal light, test point ইত্যাদি আঁকার সময়।
# real world-এ এটা কোথায় দেখা যায়: Computer graphics-এ গোল shape আঁকতে।
def draw_circle(cx, cy, r, color, segments=40): 
     
    glColor3f(*color) 
    glBegin(GL_POLYGON) 
    for i in range(segments): 
        theta = 2.0 * math.pi * i / segments 
        glVertex2f(cx + r * math.cos(theta), cy + r * math.sin(theta)) 
    glEnd() 
 
 
# কী করছে: Sky, road, car এবং traffic signal-এর পুরো scene আঁকে।
# কখন লাগছে: Main display-তে background scene দেখানোর সময়।
# real world-এ এটা কোথায় দেখা যায়: Driving simulator ও computer graphics visualization-এ।
def draw_road_scene():  
    
    glColor3f(0.50, 0.72, 0.92) 
    glBegin(GL_QUADS) 
    glVertex2f(0, 220); glVertex2f(WIDTH, 220) 
    glVertex2f(WIDTH, HEIGHT); glVertex2f(0, HEIGHT) 
    glEnd() 
 
    # 2. রাস্তা 
    glColor3f(0.25, 0.25, 0.28) 
    glBegin(GL_QUADS) 
    glVertex2f(0, 0); glVertex2f(WIDTH, 0) 
    glVertex2f(WIDTH, 220); glVertex2f(0, 220) 
    glEnd() 
 
    # 3. গাড়ি (Car Body & Wheels) 
    glColor3f(0.85, 0.20, 0.20) 
    glBegin(GL_QUADS) 
    glVertex2f(160, 90); glVertex2f(320, 90) 
    glVertex2f(320, 150); glVertex2f(160, 150) 
    glEnd() 
 
    glColor3f(0.80, 0.90, 0.98) 
    glBegin(GL_QUADS) 
    glVertex2f(190, 150); glVertex2f(280, 150) 
    glVertex2f(265, 185); glVertex2f(205, 185) 
    glEnd() 
 
    draw_circle(200, 90, 18, (0.1, 0.1, 0.1)) 
    draw_circle(280, 90, 18, (0.1, 0.1, 0.1)) 
 
    # 4. ট্রাফিক লাইট (Traffic Signal) 
    glColor3f(0.15, 0.15, 0.15) 
    glBegin(GL_QUADS) 
    glVertex2f(490, 80); glVertex2f(502, 80) 
    glVertex2f(502, 280); glVertex2f(490, 280) 
    glEnd() 
    glBegin(GL_QUADS) 
    glVertex2f(476, 280); glVertex2f(516, 280) 
    glVertex2f(516, 380); glVertex2f(476, 380) 
    glEnd() 
 
    draw_circle(496, 355, 12, (1.0, 0.2, 0.2))  # Red 
    draw_circle(496, 330, 12, (1.0, 0.8, 0.2))  # Yellow 
    draw_circle(496, 305, 12, (0.2, 0.9, 0.3))  # Green 
 
 
# --------------------------------------------------------------------------- 
# 3. Line Clipping -> Cohen-Sutherland Algorithm 
# --------------------------------------------------------------------------- 
# কী করছে: Clipping box-এর ভিতর ও চার পাশ বোঝানোর জন্য bit value রাখছে।
# কখন লাগছে: Cohen-Sutherland line clipping algorithm-এ।
# real world-এ এটা কোথায় দেখা যায়: Window-এর বাইরে থাকা graphics-এর অংশ বাদ দিতে।
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8 
 
# কী করছে: একটি point clipping box-এর কোন পাশে আছে তা নির্ধারণ করে।
# কখন লাগছে: Cohen-Sutherland algorithm line clip করার আগে।
# real world-এ এটা কোথায় দেখা যায়: Computer graphics-এর visible area নির্ধারণে।
def compute_code(x, y, xmin, ymin, xmax, ymax): 
     
    code = INSIDE 
    if x < xmin: code |= LEFT 
    elif x > xmax: code |= RIGHT 
    if y < ymin: code |= BOTTOM 
    elif y > ymax: code |= TOP 
    return code 
 
 
# কী করছে: Line-এর visible অংশ clipping box-এর মধ্যে রেখে বাকি অংশ বাদ দেয়।
# কখন লাগছে: Road lane marking-কে visual field-এর মধ্যে দেখানোর সময়।
# real world-এ এটা কোথায় দেখা যায়: Games, maps এবং 2D graphics rendering-এ।
def cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax): 
     
    code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax) 
    code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax) 
    accept = False 
 
    while True: 
        if code1 == 0 and code2 == 0: 
            accept = True 
            break 
        elif (code1 & code2) != 0: 
            break 
        else: 
            code_out = code1 if code1 != 0 else code2 
            x, y = 0.0, 0.0 
            if code_out & TOP: 
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1); y = ymax 
            elif code_out & BOTTOM: 
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1); y = ymin 
            elif code_out & RIGHT: 
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1); x = xmax 
            elif code_out & LEFT: 
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1); x = xmin 
 
            if code_out == code1: 
                x1, y1 = x, y 
                code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax) 
            else: 
                x2, y2 = x, y 
                code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax) 
 
    return (x1, y1, x2, y2) if accept else None 
 
 
# কী করছে: Road-এর lane lines তৈরি করে clipping algorithm দিয়ে visible অংশ আঁকে।
# কখন লাগছে: Visual field-এর সীমার মধ্যে road marking দেখাতে।
# real world-এ এটা কোথায় দেখা যায়: Map ও game rendering-এ।
def draw_clipped_lane_markings():  
     
    xmin = max(0, CENTER_X - vision_radius) 
    xmax = min(WIDTH, CENTER_X + vision_radius) 
    ymin = max(0, CENTER_Y - vision_radius) 
    ymax = min(HEIGHT, CENTER_Y + vision_radius) 
 
    lane_lines = [(i * 80, 50, i * 80 + 45, 50) for i in range(-1, 9)] 
 
    glColor3f(1.0, 0.9, 0.2) 
    glLineWidth(3.0) 
    glBegin(GL_LINES) 
    for (x1, y1, x2, y2) in lane_lines: 
        clipped = cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax) 
        if clipped: 
            glVertex2f(clipped[0], clipped[1]) 
            glVertex2f(clipped[2], clipped[3]) 
    glEnd() 
 
    # ক্লিপিং বাউন্ডিং বক্স আঁকা 
    if show_clip_box and glaucoma_mode: 
        glColor3f(1.0, 1.0, 0.0) 
        glLineWidth(1.5) 
        glBegin(GL_LINE_LOOP) 
        glVertex2f(xmin, ymin); glVertex2f(xmax, ymin) 
        glVertex2f(xmax, ymax); glVertex2f(xmin, ymax) 
        glEnd() 
 
 
 
# 4. Color Fill -> Tunnel Vision Scotoma Mask 
 
# কী করছে: Glaucoma-এর tunnel vision-এর মতো visual field mask তৈরি করে।
# কখন লাগছে: Glaucoma mode চালু থাকলে vision-এর বাইরের অংশ অন্ধকার করতে।
# real world-এ এটা কোথায় দেখা যায়: Medical visualization ও visual field simulation-এ।
def draw_glaucoma_scotoma():  
      
    if not glaucoma_mode: 
        return 
 
    outer_radius = math.hypot(WIDTH, HEIGHT) 
    segments = 72 
 
    glColor3f(0.02, 0.02, 0.03) 
    glBegin(GL_TRIANGLE_STRIP) 
    for i in range(segments + 1): 
        angle = 2.0 * math.pi * i / segments 
        cos_a, sin_a = math.cos(angle), math.sin(angle) 
        # ভেতরের ব্যাসার্ধ (দৃষ্টির খোলা অংশ) 
        glVertex2f(CENTER_X + vision_radius * cos_a, CENTER_Y + vision_radius * sin_a) 
        # বাইরের ব্যাসার্ধ (কালো অন্ধ অংশ) 
        glVertex2f(CENTER_X + outer_radius * cos_a, CENTER_Y + outer_radius * sin_a) 
    glEnd() 
 
    # অপটিক নার্ভের স্বাভাবিক ব্লাইন্ড স্পট (Left eye-এ বামে, Right eye-এ ডানে) 
    blind_x = CENTER_X - 85 if current_eye == "LEFT" else CENTER_X + 85 
    draw_circle(blind_x, CENTER_Y - 10, 16, (0.02, 0.02, 0.03)) 
 
 
 
# 5. Interactive Self-Perimetry Screening (Problem Solving) 
 
# কী করছে: Visual field-এর মধ্যে random test point নির্বাচন করে।
# কখন লাগছে: Perimetry test-এর প্রতিটি নতুন target তৈরি করার সময়।
# real world-এ এটা কোথায় দেখা যায়: Visual field screening test-এ।
def pick_test_target():  
    # Simulate a random perimetry target within the remaining visual field.
    global target_point 
    angle = random.uniform(0, 2 * math.pi) 
    r = random.uniform(70, MAX_RADIUS - 20) 
    target_point = (int(CENTER_X + r * math.cos(angle)), int(CENTER_Y + r * math.sin(angle))) 
 
 
# কী করছে: নতুন visual field test শুরু করার জন্য সব test variable reset করে।
# কখন লাগছে: User 'T' চাপলে test শুরু করার সময়।
# real world-এ এটা কোথায় দেখা যায়: Automated screening test শুরু করার সময়।
def start_test():  
     
    global test_mode, test_finished, test_index, test_results 
    test_mode = True 
    test_finished = False 
    test_index = 0 
    test_results = [] 
    pick_test_target() 
 
 
# কী করছে: বর্তমান vision radius থেকে কত শতাংশ visual field আছে তা হিসাব করে।
# কখন লাগছে: Screen-এ field preserved percentage দেখানোর সময়।
# real world-এ এটা কোথায় দেখা যায়: Visual field measurement ও data visualization-এ।
def get_field_percent():  
    return round(((vision_radius / MAX_RADIUS) ** 2) * 100.0, 1) 
 
 
# কী করছে: Visual field percentage অনুযায়ী একটি stage label নির্ধারণ করে।
# কখন লাগছে: Simulation-এর result screen-এ stage দেখাতে।
# real world-এ এটা কোথায় দেখা যায়: Medical screening software-এর classification display-তে।
def get_clinical_stage(pct):  
     
    if pct >= 75.0: return "Early / Mild Stage", (0.3, 0.9, 0.3) 
    elif pct >= 40.0: return "Moderate Glaucoma", (1.0, 0.8, 0.2) 
    else: return "Severe Tunnel Vision", (1.0, 0.3, 0.3) 
 
 
 
# 6. Text Display Helper 
 
# কী করছে: Screen-এ text দেখানোর জন্য helper function হিসেবে কাজ করে।
# কখন লাগছে: Test status, score ও instructions দেখানোর সময়।
# real world-এ এটা কোথায় দেখা যায়: GUI, games ও visualization software-এ।
def draw_text(x, y, text, color=(1.0, 1.0, 1.0)):  
    glColor3f(*color) 
    glRasterPos2f(x, y) 
    for ch in str(text): 
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch) if ord(ch) < 128 else ord('?')) 
 
 
 
# 7. Display Pipeline (Single Active Viewport) 
 
# কী করছে: Scene-এর সব graphics একসাথে draw করার main display function।
# কখন লাগছে: Window refresh বা redraw হওয়ার সময়।
# real world-এ এটা কোথায় দেখা যায়: প্রায় সব interactive graphics application-এর rendering pipeline-এ।
def display():  
     
    glClear(GL_COLOR_BUFFER_BIT) 
    glMatrixMode(GL_PROJECTION) 
    glLoadIdentity() 
    gluOrtho2D(0, WIDTH, 0, HEIGHT) 
    glMatrixMode(GL_MODELVIEW) 
    glLoadIdentity() 
 
    # ১. মূল দৃশ্য ও ক্লিপড রোডলাইন আঁকা 
    draw_road_scene() 
    draw_clipped_lane_markings() 
 
    # ২. গ্লুকোমা মাস্ক প্রয়োগ 
    draw_glaucoma_scotoma() 
 
    # ৩. সেন্ট্রাল ফিক্সেশন ক্রস (+) আঁকা (চোখ স্থির রাখার জন্য) 
    glColor3f(1.0, 0.2, 0.2) 
    glLineWidth(2.0) 
    glBegin(GL_LINES) 
    glVertex2f(CENTER_X - 8, CENTER_Y); glVertex2f(CENTER_X + 8, CENTER_Y) 
    glVertex2f(CENTER_X, CENTER_Y - 8); glVertex2f(CENTER_X, CENTER_Y + 8) 
    glEnd() 
 
    # ৪. টেস্টিং ইন্টারফেস ও ফলাফল 
    if test_mode: 
        draw_text(15, HEIGHT - 30, f"Testing {current_eye} Eye - Point {test_index + 1}/{NUM_TEST_POINTS}", (1, 1, 0.2)) 
        draw_text(15, HEIGHT - 50, "Keep gaze on center cross (+). Click on the yellow flash!", (0.8, 0.8, 0.8)) 
        draw_circle(target_point[0], target_point[1], 8, (1.0, 1.0, 0.2)) 
 
    elif test_finished: 
        hits = sum(1 for (_, _, h) in test_results if h) 
        score = round((hits / len(test_results)) * 100.0, 1) 
        draw_text(15, HEIGHT - 30, f"{current_eye} Eye Field Test Score: {score}%", (0.3, 1.0, 0.4)) 
        draw_text(15, HEIGHT - 50, f"Detected {hits}/{len(test_results)} points. Press 'T' to retest.", (1, 1, 1)) 
        # টেস্ট পয়েন্টগুলো আঁকা (সবুজ=দেখা গেছে, লাল=মিস) 
        for (tx, ty, hit) in test_results: 
            col = (0.2, 1.0, 0.3) if hit else (1.0, 0.2, 0.2) 
            draw_circle(tx, ty, 6, col) 
 
    else: 
        field_pct = get_field_percent() 
        stage_name, stage_col = get_clinical_stage(field_pct) 
        mode_str = "Glaucoma Tunnel Vision" if glaucoma_mode else "Normal Healthy Vision" 
        draw_text(15, HEIGHT - 30, f"Glaucoma Visual Field Research Tool - {current_eye} EYE", (0.4, 0.8, 1.0)) 
        draw_text(15, HEIGHT - 50, f"Mode: {mode_str} | Field Preserved: {field_pct}%", (1, 1, 1)) 
        draw_text(15, HEIGHT - 70, f"Clinical Stage: {stage_name}", stage_col) 
 
    # নিচের স্ট্যাটাস বার 
    draw_text(15, 15, f"Keys: [L] Left Eye  [R] Right Eye  [V] Normal/Glaucoma  [+/-] Radius  [T] Test  [Q] Exit", (0.7, 0.8, 0.9)) 
 
    glutSwapBuffers() 
 
 
 
# 8. User Interaction (Keyboard & Mouse) 
 
# কী করছে: Keyboard থেকে user-এর command গ্রহণ করে।
# কখন লাগছে: Eye change, glaucoma mode, radius, test ও exit control করার সময়।
# real world-এ এটা কোথায় দেখা যায়: Games, simulator ও interactive applications-এ।
def keyboard(key, x, y):  
    global vision_radius, current_eye, glaucoma_mode, show_clip_box 
 
    if key in (b'l', b'L'): 
        current_eye = "LEFT" 
    elif key in (b'r', b'R'): 
        current_eye = "RIGHT" 
    elif key in (b'v', b'V'): 
        glaucoma_mode = not glaucoma_mode 
    elif key in (b'+', b'='): 
        vision_radius = min(MAX_RADIUS, vision_radius + 15) 
    elif key == b'-': 
        vision_radius = max(MIN_RADIUS, vision_radius - 15) 
    elif key in (b'c', b'C'): 
        show_clip_box = not show_clip_box 
    elif key in (b't', b'T'): 
        start_test() 
    elif key in (b'q', b'Q', b'\x1b'): 
        glutLeaveMainLoop() 
 
    glutPostRedisplay() 
 
 
# কী করছে: Mouse click-এর position নিয়ে test target hit হয়েছে কিনা check করে।
# কখন লাগছে: Perimetry test চলার সময় user click করলে।
# real world-এ এটা কোথায় দেখা যায়: Interactive testing ও GUI applications-এ।
def mouse(button, state, x, y):  
    global test_index, test_mode, test_finished, test_results 
    if not test_mode or button != GLUT_LEFT_BUTTON or state != GLUT_DOWN: 
        return 
 
    gl_x = x 
    gl_y = HEIGHT - y  # OpenGL inverted Y coordinate 
 
    tx, ty = target_point 
    dist = math.hypot(gl_x - tx, gl_y - ty) 
    hit = (dist <= HIT_TOLERANCE) 
 
    test_results.append((tx, ty, hit)) 
    test_index += 1 
 
    if test_index >= NUM_TEST_POINTS: 
        test_mode = False 
        test_finished = True 
    else: 
        pick_test_target() 
 
    glutPostRedisplay() 
 
# 9. Initialization & Main Loop 
# কী করছে: OpenGL/GLUT initialize করে window, callback এবং main loop চালু করে।
# কখন লাগছে: Program শুরু হওয়ার সময়।
# real world-এ এটা কোথায় দেখা যায়: OpenGL-based graphics application চালু করতে।
def main():  
    glutInit() 
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB) 
    glutInitWindowSize(WIDTH, HEIGHT) 
    glutCreateWindow(b"Glaucoma Visual Field Research Visualizer - Track B") 
 
    glClearColor(0.05, 0.05, 0.07, 1.0) 
    glutDisplayFunc(display) 
    glutKeyboardFunc(keyboard) 
    glutMouseFunc(mouse) 
    glutMainLoop() 
 
 
if __name__ == "__main__": 
    main()