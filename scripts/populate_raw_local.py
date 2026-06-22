import os
import random
from PIL import Image, ImageDraw

RAW_DIR = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/vision_bin_custom_dataset/raw_images"
TEMP_DIR = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/temp_assets"

# Define the 6 target subfolders
subfolders = {
    0: "0_plastic_pet_hdpe",
    1: "1_paper_cardboard",
    2: "2_metal_aluminum_steel",
    3: "3_glass_bottles_jars",
    4: "4_organic_food_waste",
    5: "5_ewaste_hazardous"
}

# Ensure folders exist
for folder in subfolders.values():
    os.makedirs(os.path.join(RAW_DIR, folder), exist_ok=True)

# Procedural Fallbacks for Foreground objects (matching class IDs)
def make_procedural_foreground(class_id):
    img = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if class_id == 0:  # Plastic bottle
        draw.rounded_rectangle([90, 60, 210, 270], radius=25, fill=(173, 216, 230, 200), outline=(70, 130, 180, 255), width=5)
        draw.rectangle([120, 20, 180, 60], fill=(173, 216, 230, 200), outline=(70, 130, 180, 255), width=5)
        draw.rectangle([115, 10, 185, 25], fill=(30, 144, 255, 255))
        draw.rectangle([100, 120, 200, 200], fill=(240, 240, 240, 255))
        
    elif class_id == 1:  # Paper / Cardboard box
        draw.rectangle([60, 60, 240, 240], fill=(210, 180, 140, 255), outline=(139, 69, 19, 255), width=6)
        draw.line([(60, 150), (240, 150)], fill=(139, 69, 19, 255), width=4)
        draw.line([(150, 60), (150, 240)], fill=(139, 69, 19, 255), width=4)
        
    elif class_id == 2:  # Metal aluminum can
        draw.rounded_rectangle([75, 45, 225, 255], radius=15, fill=(192, 192, 192, 255), outline=(128, 128, 128, 255), width=6)
        draw.rectangle([81, 105, 219, 195], fill=(255, 0, 0, 255))
        draw.ellipse([135, 22, 165, 42], fill=(128, 128, 128, 255), outline=(64, 64, 64, 255), width=2)
        
    elif class_id == 3:  # Glass jar
        draw.rounded_rectangle([80, 75, 220, 260], radius=30, fill=(144, 238, 144, 150), outline=(46, 139, 87, 255), width=6)
        draw.rectangle([120, 30, 180, 75], fill=(144, 238, 144, 150), outline=(46, 139, 87, 255), width=6)
        
    elif class_id == 4:  # Organic food / banana
        draw.arc([(45, 45), (255, 255)], 30, 150, fill=(255, 223, 0, 255), width=35)
        draw.ellipse([217, 187, 240, 210], fill=(101, 67, 33, 255))
        
    elif class_id == 5:  # E-waste / Keyboard
        draw.rounded_rectangle([45, 90, 255, 210], radius=8, fill=(50, 50, 50, 255), outline=(100, 100, 100, 255), width=5)
        for row in range(112, 195, 22):
            for col in range(60, 240, 22):
                draw.rectangle([col, row, col + 15, row + 12], fill=(220, 220, 220, 255))
                
    return img

# Load backgrounds
bg_types = ["grass", "pavement", "wood"]
bg_images = {}

# Sourcing local backgrounds
for bg in bg_types:
    bg_path = os.path.join(TEMP_DIR, f"bg_{bg}.jpg")
    if os.path.exists(bg_path):
        try:
            bg_images[bg] = Image.open(bg_path).resize((640, 640))
        except Exception as e:
            print(f"Error loading local background '{bg}': {e}")

# Fallback background generators
def make_procedural_background(bg_type):
    img = Image.new("RGB", (640, 640), color=(128, 128, 128))
    draw = ImageDraw.Draw(img)
    if bg_type == "grass":
        img = Image.new("RGB", (640, 640), color=(34, 139, 34))
        draw = ImageDraw.Draw(img)
        for _ in range(200):
            x = random.randint(0, 640)
            y = random.randint(0, 640)
            draw.line([(x, y), (x + random.randint(-5, 5), y - random.randint(5, 20))], fill=(50, 205, 50), width=random.randint(1, 3))
    elif bg_type == "pavement":
        img = Image.new("RGB", (640, 640), color=(169, 169, 169))
        draw = ImageDraw.Draw(img)
        for y in range(0, 640, 40):
            draw.line([(0, y), (640, y)], fill=(105, 105, 105), width=2)
            offset = 20 if (y // 40) % 2 == 0 else 0
            for x in range(offset, 640, 80):
                draw.line([(x, y), (x, y + 40)], fill=(105, 105, 105), width=2)
    elif bg_type == "wood":
        img = Image.new("RGB", (640, 640), color=(139, 69, 19))
        draw = ImageDraw.Draw(img)
        for _ in range(50):
            y = random.randint(0, 640)
            draw.arc([(-100, y - 50), (740, y + 50)], 0, 180, fill=(101, 67, 33), width=random.randint(1, 4))
    return img

for bg in bg_types:
    if bg not in bg_images:
        bg_images[bg] = make_procedural_background(bg)

# Map class name key to asset filenames
asset_map = {
    0: "fg_bottle.png",
    1: "procedural",
    2: "fg_can.png",
    3: "procedural",
    4: "fg_apple.png",
    5: "fg_keyboard.png"
}

# Generate 10 images per class folder
for class_id, folder_name in subfolders.items():
    class_dir = os.path.join(RAW_DIR, folder_name)
    print(f"Generating raw images inside: {folder_name}...")
    
    # Load raw object PNG
    fg_file = asset_map[class_id]
    fg_path = os.path.join(TEMP_DIR, fg_file)
    
    fg_base = None
    if fg_file != "procedural" and os.path.exists(fg_path):
        try:
            fg_base = Image.open(fg_path).convert("RGBA")
        except Exception as e:
            print(f"Error loading {fg_file}: {e}")
            
    if fg_base is None:
        # Fallback to custom procedural vector shape
        fg_base = make_procedural_foreground(class_id)
        
    for i in range(10):
        # Pick background
        bg_name = random.choice(bg_types)
        composite = bg_images[bg_name].copy()
        
        # Apply random transforms to foreground
        scale = random.uniform(0.7, 1.3)
        w, h = fg_base.size
        fg_scaled = fg_base.resize((int(w * scale), int(h * scale)))
        fg_rotated = fg_scaled.rotate(random.randint(0, 360), expand=True)
        
        # Position randomly
        max_x = 640 - fg_rotated.width
        max_y = 640 - fg_rotated.height
        px = random.randint(0, max_x) if max_x > 0 else 0
        py = random.randint(0, max_y) if max_y > 0 else 0
        
        # Paste object
        composite.paste(fg_rotated, (px, py), fg_rotated)
        
        # Save raw image
        out_filename = os.path.join(class_dir, f"raw_waste_{class_id}_{i+1}.jpg")
        composite.save(out_filename, "JPEG")

print("\n[SUCCESS] Raw category folders populated with 10 composite raw images each! ready for labeling.")
