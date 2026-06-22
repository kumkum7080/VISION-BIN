import streamlit as st
import os
import time
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Try importing YOLO, fall back to mock prediction if unavailable
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

# Set page config
st.set_page_config(
    page_title="Vision Bin | AI Camera Dashboard",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 1. PREMIUM CUSTOM CSS & THEME INJECTION
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;700&display=swap');
    
    /* Main container styling */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #312e81;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .dashboard-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        margin: 0;
        letter-spacing: -0.05em;
    }
    
    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Card styling */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        color: #f8fafc;
        font-size: 1.3rem;
        margin-bottom: 1rem;
        border-left: 4px solid #00f2fe;
        padding-left: 10px;
    }
    
    /* Quick KPI cards */
    .kpi-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .kpi-card {
        flex: 1;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(0, 242, 254, 0.15);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #00f2fe;
    }
    
    .kpi-val {
        font-size: 1.5rem;
        font-weight: 800;
        color: #00f2fe;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .kpi-lbl {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.2rem;
    }

    /* Class pill indicators */
    .class-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 4px;
        color: #0f172a;
    }
    
    /* Custom buttons style */
    .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #0f172a !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.5) !important;
    }
    
    /* Customize table styling */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }
    .custom-table th {
        background-color: rgba(15, 23, 42, 0.8);
        color: #94a3b8;
        font-weight: 600;
        text-align: left;
        padding: 10px;
        border-bottom: 2px solid rgba(255,255,255,0.08);
        font-size: 0.85rem;
        text-transform: uppercase;
    }
    .custom-table td {
        padding: 12px 10px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        color: #cbd5e1;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# 2. COLOR SCHEME FOR DETECTED CLASSES
# -----------------------------------------------------------------------------
CLASS_META = {
    0: {"name": "Plastic", "color": "#00f2fe", "desc": "PET, HDPE bottles, clean films"},
    1: {"name": "Paper", "color": "#ffb347", "desc": "Cardboard boxes, folded sheets"},
    2: {"name": "Metal", "color": "#ff4e50", "desc": "Aluminum beverage cans, steel scrap"},
    3: {"name": "Glass", "color": "#2eeb9a", "desc": "Transparent & tinted bottles, food jars"},
    4: {"name": "Organic", "color": "#8bc34a", "desc": "Wet kitchen waste, banana peels, foods"},
    5: {"name": "E-waste", "color": "#b19ffb", "desc": "Batteries, keyboard parts, cell phones"}
}

# -----------------------------------------------------------------------------
# 3. DIRECTORY SETUP AND PATH CONFIGURATIONS
# -----------------------------------------------------------------------------
PROJECT_ROOT = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN"
WEIGHTS_PATH = os.path.join(PROJECT_ROOT, "runs/vision_bin_baseline_prod/weights/best.pt")
DATASET_PATH = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/vision_bin_public_dataset"

# -----------------------------------------------------------------------------
# 4. LOAD YOLO MODEL (WITH ROBUST FALLBACK)
# -----------------------------------------------------------------------------
# Helper to map COCO classes to Vision Bin classes
def map_coco_to_vision_bin(cls_name):
    cls_name = cls_name.lower()
    if cls_name == "bottle":
        return 0, "Plastic (COCO Bottle)"
    elif cls_name in ["banana"]:
        return 4, "Organic (COCO Banana)"
    elif cls_name in ["apple"]:
        return 4, "Organic (COCO Apple)"
    elif cls_name in ["orange", "broccoli", "carrot", "sandwich"]:
        return 4, f"Organic (COCO {cls_name.capitalize()})"
    elif cls_name in ["keyboard", "laptop", "mouse", "remote"]:
        return 5, f"E-waste (COCO {cls_name.capitalize()})"
    elif cls_name in ["cell phone"]:
        return 5, "E-waste (COCO Phone)"
    elif cls_name in ["book", "cup", "bowl"]:
        return 1, f"Paper (COCO {cls_name.capitalize()})"
    elif cls_name in ["fork", "knife", "spoon", "scissors"]:
        return 2, f"Metal (COCO {cls_name.capitalize()})"
    elif cls_name in ["wine glass"]:
        return 3, f"Glass (COCO {cls_name.capitalize()})"
    else:
        return 0, f"Other (COCO {cls_name.capitalize()})"

@st.cache_resource
def get_model(choice):
    if not YOLO_AVAILABLE:
        st.warning("⚠️ Ultralytics package is missing. Running in Simulation Mode.")
        return None
        
    if choice == "Custom Waste Model (6 Classes)":
        if os.path.exists(WEIGHTS_PATH):
            try:
                model = YOLO(WEIGHTS_PATH)
                return {"model": model, "type": "Trained YOLOv11 (best.pt)", "is_custom": True}
            except Exception as e:
                st.error(f"Error loading custom weights: {e}. Falling back to default.")
        else:
            st.warning("Custom weights (best.pt) not found. Falling back to COCO.")
            
    # Load pre-trained COCO model
    try:
        model = YOLO("yolo11n.pt")
        return {"model": model, "type": "Pre-trained YOLOv11n (COCO)", "is_custom": False}
    except Exception as e:
        st.error(f"Could not load pre-trained YOLO: {e}")
        return None

# -----------------------------------------------------------------------------
# 5. DRAW BOUNDING BOXES UTILITY
# -----------------------------------------------------------------------------
def draw_predictions(image, boxes, threshold, is_custom, names_dict):
    """
    Draws custom styled bounding boxes and labels onto a PIL image.
    """
    draw_img = image.copy()
    draw = ImageDraw.Draw(draw_img)
    
    # Try loading a cleaner font, fall back to default
    try:
        font = ImageFont.load_default()
    except IOError:
        font = None
        
    width, height = draw_img.size
    
    detections = []
    
    for box in boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        
        if conf < threshold:
            continue
            
        xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
        
        if is_custom:
            meta = CLASS_META.get(cls_id, {"name": f"Class {cls_id}", "color": "#ffffff"})
            color = meta["color"]
            name = meta["name"]
        else:
            cls_name = names_dict.get(cls_id, f"Class {cls_id}")
            mapped_id, label_name = map_coco_to_vision_bin(cls_name)
            meta = CLASS_META.get(mapped_id, {"name": label_name, "color": "#ffffff"})
            color = meta["color"]
            name = label_name
            
        # Convert color hex to RGB
        rgb_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # Draw bounding box rectangle
        draw.rectangle(xyxy, outline=rgb_color, width=4)
        
        # Bounding box corners
        x1, y1, x2, y2 = xyxy
        corner_len = min(20, (x2-x1)/4, (y2-y1)/4)
        draw.line([(x1, y1), (x1 + corner_len, y1)], fill=rgb_color, width=7)
        draw.line([(x1, y1), (x1, y1 + corner_len)], fill=rgb_color, width=7)
        draw.line([(x2, y1), (x2 - corner_len, y1)], fill=rgb_color, width=7)
        draw.line([(x2, y1), (x2, y1 + corner_len)], fill=rgb_color, width=7)
        draw.line([(x1, y2), (x1 + corner_len, y2)], fill=rgb_color, width=7)
        draw.line([(x1, y2), (x1, y2 - corner_len)], fill=rgb_color, width=7)
        draw.line([(x2, y2), (x2 - corner_len, y2)], fill=rgb_color, width=7)
        draw.line([(x2, y2), (x2, y2 - corner_len)], fill=rgb_color, width=7)

        # Label box drawing
        label_text = f"{name} {conf:.0%}"
        text_bbox = draw.textbbox((0, 0), label_text, font=font)
        text_w = text_bbox[2] - text_bbox[0] + 12
        text_h = text_bbox[3] - text_bbox[1] + 8
        
        draw.rectangle([x1, max(0, y1 - text_h), x1 + text_w, y1], fill=rgb_color)
        draw.text((x1 + 6, max(0, y1 - text_h) + 2), label_text, fill=(15, 23, 42), font=font)
        
        detections.append({
            "class_id": cls_id,
            "name": name,
            "confidence": conf,
            "bbox": [round(x) for x in xyxy],
            "color": color
        })
        
    return draw_img, detections

# -----------------------------------------------------------------------------
# 6. HEADER RENDER
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="dashboard-header">
        <h1 class="dashboard-title">📷 VISION BIN AI CAMERA</h1>
        <div class="dashboard-subtitle">Real-time smart waste identification model checking interface. Powered by YOLOv11 & Composited Datasets.</div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# 7. SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top:0; color:#f8fafc; font-family:\'Space Grotesk\'">⚙️ CONFIGURATION</h3>', unsafe_allow_html=True)
    
    # Model Selection Toggle
    model_choice = st.radio(
        "Active AI Model",
        ["Custom Waste Model (6 Classes)", "Pre-trained COCO Model (80 Classes)"],
        index=0,
        help="Switch between your custom-trained 1-epoch model and the pre-trained 80-class COCO model (which includes highly accurate bottles, cans, etc.)."
    )
    
    # Confidence Slider
    conf_thresh = st.slider(
        "Confidence Threshold", 
        min_value=0.05, 
        max_value=1.00, 
        value=0.25, 
        step=0.05,
        help="Filter out detections with confidence scores lower than this threshold."
    )
    
    st.markdown("---")
    
    # Dynamic Model Load
    model_wrapper = get_model(model_choice)
    model_name = model_wrapper["type"] if model_wrapper else "Simulation (No YOLO)"
    
    st.markdown(
        f"""
        <div class="kpi-card" style="margin-bottom:1rem; border-color:#8bc34a;">
            <div class="kpi-val" style="font-size:1rem; color:#8bc34a;">{model_name}</div>
            <div class="kpi-lbl">Active AI Engine</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display target classes
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top:0; color:#f8fafc; font-family:\'Space Grotesk\'">🏷️ TARGET WASTE CLASSES</h3>', unsafe_allow_html=True)
    
    for cid, val in CLASS_META.items():
        st.markdown(
            f"""
            <div style="margin-bottom: 8px;">
                <span class="class-badge" style="background-color:{val['color']}">{val['name']}</span>
                <span style="font-size:0.8rem; color:#94a3b8;">({val['desc']})</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. MAIN COLUMN LAYOUT
# -----------------------------------------------------------------------------
col_input, col_output = st.columns([5, 7])

# Left Column - Inputs
with col_input:
    st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📥 IMAGE SOURCE SELECTION</div>', unsafe_allow_html=True)
    
    source_tab = st.tabs(["📁 Sample Presets", "📤 Upload Custom Image", "📷 Live Webcam"])
    
    selected_image = None
    image_name = ""
    
    # Tab 1: Presets
    with source_tab[0]:
        st.write("Test the model using synthetic composite waste images from the test dataset split:")
        
        # Check if dataset images exist
        test_img_dir = os.path.join(DATASET_PATH, "test/images")
        if os.path.exists(test_img_dir):
            preset_files = [f for f in os.listdir(test_img_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
            preset_files = sorted(preset_files)[:10]  # Take up to 10
            
            if preset_files:
                selected_preset = st.selectbox("Choose a preset image", preset_files)
                preset_path = os.path.join(test_img_dir, selected_preset)
                try:
                    selected_image = Image.open(preset_path)
                    image_name = selected_preset
                    st.image(selected_image, caption=f"Selected Preset: {selected_preset}", use_column_width=True)
                except Exception as e:
                    st.error(f"Error loading preset: {e}")
            else:
                st.info("No images found in the dataset folder. Presets are unavailable.")
        else:
            st.info("Public dataset test path not found. Run harmonize_dataset.py to build presets.")
            
    # Tab 2: Upload Image
    with source_tab[1]:
        uploaded_file = st.file_uploader("Upload an image of a waste item...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            try:
                selected_image = Image.open(uploaded_file).convert("RGB")
                image_name = uploaded_file.name
                st.image(selected_image, caption="Uploaded Image", use_column_width=True)
            except Exception as e:
                st.error(f"Error loading uploaded image: {e}")
                
    # Tab 3: Webcam Input
    with source_tab[2]:
        st.write("Capture a live frame from your camera feed:")
        camera_file = st.camera_input("Take a photo of the waste item")
        if camera_file is not None:
            try:
                selected_image = Image.open(camera_file).convert("RGB")
                image_name = "webcam_capture.jpg"
            except Exception as e:
                st.error(f"Error loading camera capture: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# Right Column - Output & Live Inference
with col_output:
    st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚡ REAL-TIME INFERENCE VIEWER</div>', unsafe_allow_html=True)
    
    if selected_image is not None:
        # Load and run predictions
        if model_wrapper:
            model = model_wrapper["model"]
            
            # Start timer
            start_time = time.time()
            
            # Run YOLO prediction
            results = model.predict(selected_image, verbose=False)
            boxes = results[0].boxes
            
            # Calculate inference time
            inference_time_ms = (time.time() - start_time) * 1000
            
            # Draw predictions on image
            annotated_img, detections = draw_predictions(
                selected_image, 
                boxes, 
                conf_thresh, 
                is_custom=model_wrapper.get("is_custom", True), 
                names_dict=model.names
            )
            
            # Display image
            st.image(annotated_img, caption=f"Model Annotations - {image_name}", use_column_width=True)
            
            # Render KPIs
            st.markdown(
                f"""
                <div class="kpi-container">
                    <div class="kpi-card">
                        <div class="kpi-val">{len(detections)}</div>
                        <div class="kpi-lbl">Objects Detected</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-val">{inference_time_ms:.1f} ms</div>
                        <div class="kpi-lbl">Inference Latency</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-val">{(1000 / max(1, inference_time_ms)):.1f}</div>
                        <div class="kpi-lbl">Target FPS</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Render detections list table
            if detections:
                st.markdown('<h4 style="margin-top: 1.5rem; color:#f8fafc; font-family:\'Space Grotesk\'">🔍 Detections List</h4>', unsafe_allow_html=True)
                
                table_rows = ""
                for det in detections:
                    # bounding box dimensions
                    bbox_str = f"[{det['bbox'][0]}, {det['bbox'][1]}, {det['bbox'][2]}, {det['bbox'][3]}]"
                    width_px = det['bbox'][2] - det['bbox'][0]
                    height_px = det['bbox'][3] - det['bbox'][1]
                    area_px = f"{width_px}x{height_px} px"
                    
                    table_rows += f"""
                    <tr>
                        <td><span class="class-badge" style="background-color:{det['color']}">{det['name']}</span></td>
                        <td style="font-weight:700; color:{det['color']}">{det['confidence']:.1%}</td>
                        <td style="font-family:'Courier New', monospace;">{bbox_str}</td>
                        <td>{area_px}</td>
                    </tr>
                    """
                    
                st.markdown(
                    f"""
                    <table class="custom-table">
                        <thead>
                            <tr>
                                <th>Class</th>
                                <th>Confidence</th>
                                <th>Bounding Box [x1,y1,x2,y2]</th>
                                <th>Scale Size</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info(f"No objects detected above the {conf_thresh:.0%} confidence threshold.")
        else:
            st.error("YOLO Model is not loaded. Please install requirements or place model weights correctly.")
    else:
        # Placeholder when no image is loaded
        st.markdown(
            """
            <div style="text-align: center; padding: 5rem 2rem; border: 2px dashed rgba(255, 255, 255, 0.1); border-radius: 12px; background: rgba(15, 23, 42, 0.3);">
                <span style="font-size: 3rem; color: #64748b;">📷</span>
                <h3 style="color: #94a3b8; font-family: 'Space Grotesk', sans-serif; margin-top: 1rem;">No Image Loaded</h3>
                <p style="color: #64748b; font-size: 0.95rem; max-width: 400px; margin: 0.5rem auto;">
                    Select a sample preset, upload a custom picture, or activate your webcam to trigger real-time AI object detection.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. COMPOSITE DATASET DETAILS SECTION
# -----------------------------------------------------------------------------
st.markdown('<div class="glass-card" style="margin-top: 2rem;">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📖 DATASET COMPOSITION METHODOLOGY</div>', unsafe_allow_html=True)

st.markdown(
    """
    To ensure the Vision Bin camera-based AI model can classify items correctly in realistic, non-plain settings, we trained it on a specialized **synthetic compositor dataset** compiled by 
    <a href="file:///C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/scripts/harmonize_dataset.py" style="color:#00f2fe; text-decoration:none; font-weight:600;">harmonize_dataset.py</a>.
    
    Here is how the data composition works:
    
    1. <b>Cluttered Background Sourcing:</b> High-resolution textures representing real deployment scenarios—including lawns/grass blades, brick pavements, and wood grains—were sourced from Wikimedia Commons.
    2. <b>Foreground Isolation:</b> High-fidelity transparent PNG outlines of typical waste categories (Class 0: Plastic bottle, Class 1: Paper box, Class 2: Aluminum can, Class 4: Apple fruit, Class 5: Keyboard) were downloaded or procedurally generated using PIL vector masks.
    3. <b>Multi-Object Random Composition:</b> Rather than centering a single item on a sterile background, the compositor pastes between <b>1 to 4 random objects</b> onto a random background texture.
    4. <b>Dynamic Geometric Augmentation:</b> Objects are dynamically scaled (from 0.6x to 1.2x) and rotated (0° to 360°), and alpha channels are blended to simulate overlap and partial occlusion.
    5. <b>Exact Bounding Box Mapping:</b> The bounding coordinates are calculated pixel-precisely from the rotated non-transparent margins, allowing YOLOv11 to learn the spatial separation of multiple overlapping waste items.
    
    This technique prevents the model from overfitting to simple backgrounds, allowing robust classification in real-world scenarios.
    """,
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)
