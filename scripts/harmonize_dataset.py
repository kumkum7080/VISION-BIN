import os
import random
import urllib.request
from PIL import Image, ImageDraw, ImageFilter

# 1. Directory Structure Definitions
OUTPUT_DIR = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/vision_bin_public_dataset"
SPLITS = ["train", "val", "test"]

# Ensure directories exist
for split in SPLITS:
    for sub in ["images", "labels"]:
        os.makedirs(os.path.join(OUTPUT_DIR, split, sub), exist_ok=True)

# 2. Stable Public URLs for Download (Wikimedia Commons)
URLS = {
    "bg_grass": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Lawn_with_grass_blades_close-up.jpg/640px-Lawn_with_grass_blades_close-up.jpg",
    "bg_pavement": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Red_pavement_stones.jpg/640px-Red_pavement_stones.jpg",
    "bg_wood": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Wood_grain_texture.jpg/640px-Wood_grain_texture.jpg",
    "fg_bottle": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Plastic_bottle_PET_1.png/240px-Plastic_bottle_PET_1.png",
    "fg_can": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Empty_aluminum_drink_can.png/200px-Empty_aluminum_drink_can.png",
    "fg_apple": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Red_Apple.jpg/240px-Red_Apple.jpg",
    "fg_keyboard": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Computer_keyboard.png/320px-Computer_keyboard.png"
}

# 3. Procedural Fallback Generators (PIL ImageDraw)
def make_procedural_background(bg_type):
    img = Image.new("RGB", (640, 640), color=(128, 128, 128))
    draw = ImageDraw.Draw(img)
    
    if bg_type == "grass":
        # Draw green textured pattern
        img = Image.new("RGB", (640, 640), color=(34, 139, 34))
        draw = ImageDraw.Draw(img)
        for _ in range(200):
            x = random.randint(0, 640)
            y = random.randint(0, 640)
            length = random.randint(5, 20)
            draw.line([(x, y), (x + random.randint(-5, 5), y - length)], fill=(50, 205, 50), width=random.randint(1, 3))
            
    elif bg_type == "pavement":
        # Draw grid patterns simulating brick pavement
        img = Image.new("RGB", (640, 640), color=(169, 169, 169))
        draw = ImageDraw.Draw(img)
        for y in range(0, 640, 40):
            draw.line([(0, y), (640, y)], fill=(105, 105, 105), width=2)
            offset = 20 if (y // 40) % 2 == 0 else 0
            for x in range(offset, 640, 80):
                draw.line([(x, y), (x, y + 40)], fill=(105, 105, 105), width=2)
                
    elif bg_type == "wood":
        # Draw wood grain gradient lines
        img = Image.new("RGB", (640, 640), color=(139, 69, 19))
        draw = ImageDraw.Draw(img)
        for _ in range(50):
            y = random.randint(0, 640)
            draw.arc([(-100, y - 50), (740, y + 50)], 0, 180, fill=(101, 67, 33), width=random.randint(1, 4))
            
    return img

def make_procedural_foreground(class_id):
    # Generates a transparent PNG of the object
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if class_id == 0:  # Plastic (PET/HDPE bottle)
        # Transparent blue bottle body
        draw.rounded_rectangle([60, 40, 140, 180], radius=15, fill=(173, 216, 230, 180), outline=(70, 130, 180, 255), width=3)
        # Bottle neck
        draw.rectangle([80, 15, 120, 40], fill=(173, 216, 230, 180), outline=(70, 130, 180, 255), width=3)
        # Blue cap
        draw.rectangle([75, 10, 125, 20], fill=(30, 144, 255, 255))
        # Internal label
        draw.rectangle([65, 80, 135, 130], fill=(240, 240, 240, 255))
        draw.text((85, 100), "PET", fill=(0, 0, 0, 255))
        
    elif class_id == 1:  # Paper / Cardboard box
        # Brown cardboard box outline
        draw.rectangle([40, 40, 160, 160], fill=(210, 180, 140, 255), outline=(139, 69, 19, 255), width=4)
        # Top tape line
        draw.line([(40, 100), (160, 100)], fill=(139, 69, 19, 255), width=3)
        draw.line([(100, 40), (100, 160)], fill=(139, 69, 19, 255), width=3)
        
    elif class_id == 2:  # Metal (aluminum can)
        # Silver cylinder body
        draw.rounded_rectangle([50, 30, 150, 170], radius=10, fill=(192, 192, 192, 255), outline=(128, 128, 128, 255), width=4)
        # Coca-cola red stripe
        draw.rectangle([54, 70, 146, 130], fill=(255, 0, 0, 255))
        # Pull tab ring at the top
        draw.ellipse([90, 15, 110, 28], fill=(128, 128, 128, 255), outline=(64, 64, 64, 255), width=1)
        
    elif class_id == 3:  # Glass (bottle/jar)
        # Transparent green glass outline
        draw.rounded_rectangle([55, 50, 145, 175], radius=20, fill=(144, 238, 144, 120), outline=(46, 139, 87, 255), width=4)
        # Bottle neck
        draw.rectangle([82, 20, 118, 50], fill=(144, 238, 144, 120), outline=(46, 139, 87, 255), width=4)
        
    elif class_id == 4:  # Organic (fruit/banana)
        # Yellow crescent banana shape
        draw.arc([(30, 30), (170, 170)], 30, 150, fill=(255, 223, 0, 255), width=25)
        # Brown tip
        draw.ellipse([145, 125, 160, 140], fill=(101, 67, 33, 255))
        
    elif class_id == 5:  # E-waste (electronic component / keyboard)
        # Dark grey keyboard plate
        draw.rounded_rectangle([30, 60, 170, 140], radius=5, fill=(50, 50, 50, 255), outline=(100, 100, 100, 255), width=3)
        # Draw white grid keys
        for row in range(75, 130, 15):
            for col in range(40, 160, 15):
                draw.rectangle([col, row, col + 10, row + 8], fill=(220, 220, 220, 255))
                
    return img

# Load or generate backgrounds and foregrounds
print("Sourcing elements...")
bg_images = {}
fg_images = {}

temp_dir = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/temp_assets"
os.makedirs(temp_dir, exist_ok=True)

def download_file(url, local_path):
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    )
    with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out_file:
        out_file.write(response.read())

# Fetch backgrounds
for key, url in URLS.items():
    local_path = os.path.join(temp_dir, f"{key}.jpg" if key.startswith("bg") else f"{key}.png")
    if not os.path.exists(local_path):
        try:
            print(f"Downloading {key}...")
            download_file(url, local_path)
        except Exception as e:
            print(f"Failed download for {key}: {e}. Falling back to procedural generation.")
            
    # Load image
    if os.path.exists(local_path):
        try:
            img = Image.open(local_path)
            if key.startswith("bg"):
                bg_images[key.split("_")[1]] = img.resize((640, 640))
            else:
                fg_images[key.split("_")[1]] = img.convert("RGBA")
        except Exception as e:
            print(f"Error loading {key}: {e}")

# Ensure procedural fallbacks are loaded for missing components
for bg_type in ["grass", "pavement", "wood"]:
    if bg_type not in bg_images:
        bg_images[bg_type] = make_procedural_background(bg_type)

classes_map = {
    0: "bottle",    # Plastic
    1: "box",       # Paper
    2: "can",       # Metal
    3: "glass",     # Glass (fall back to procedural)
    4: "apple",     # Organic
    5: "keyboard"   # E-waste
}

for cid, cname in classes_map.items():
    if cname in fg_images:
        # If it's a downloaded photo (like apple/bottle), remove white background if needed
        # By converting near-white pixels to transparent
        img = fg_images[cname]
        if img.mode != 'RGBA':
            img = img.convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            # Mask out white backgrounds
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        fg_images[cid] = img.resize((150, 150))
    else:
        # Generate clean vector shape
        fg_images[cid] = make_procedural_foreground(cid)

# =========================================================================
# 4. COMPOSITION PIPELINE
# =========================================================================
print("Composing synthetic object-in-scene data splits...")

# Generate dataset counts: train=120, val=20, test=10
dataset_sizes = {"train": 120, "val": 20, "test": 10}

for split, size in dataset_sizes.items():
    print(f"Building split '{split}' with {size} images...")
    for idx in range(size):
        # 1. Pick a random background
        bg_name = random.choice(list(bg_images.keys()))
        composite = bg_images[bg_name].copy()
        
        labels_list = []
        num_objects = random.randint(1, 4)  # 1 to 4 objects per image (testing multi-object!)
        
        # Keep track of occupied spots to prevent excessive stacking
        placed_positions = []
        
        for _ in range(num_objects):
            class_id = random.randint(0, 5)
            fg = fg_images[class_id]
            
            # Apply random scaling
            scale_factor = random.uniform(0.6, 1.2)
            w_fg, h_fg = fg.size
            new_w = int(w_fg * scale_factor)
            new_h = int(h_fg * scale_factor)
            fg_scaled = fg.resize((new_w, new_h))
            
            # Apply random rotation
            rot_angle = random.randint(0, 360)
            fg_rot = fg_scaled.rotate(rot_angle, expand=True)
            
            # Find a placement coordinate
            max_x = 640 - fg_rot.width
            max_y = 640 - fg_rot.height
            if max_x <= 0 or max_y <= 0:
                continue
                
            # Place in different quadrants if possible
            px = random.randint(0, max_x)
            py = random.randint(0, max_y)
            
            # Paste the object onto background using alpha channel
            composite.paste(fg_rot, (px, py), fg_rot)
            
            # Retrieve exact bounding box dimensions of rotated non-transparent contents
            rotated_bbox = fg_rot.getbbox()
            if rotated_bbox is None:
                rotated_bbox = (0, 0, fg_rot.width, fg_rot.height)
                
            x_min = px + rotated_bbox[0]
            y_min = py + rotated_bbox[1]
            x_max = px + rotated_bbox[2]
            y_max = py + rotated_bbox[3]
            
            # Normalize to YOLO format
            x_center = (x_min + x_max) / (2.0 * 640)
            y_center = (y_min + y_max) / (2.0 * 640)
            width = (x_max - x_min) / 640
            height = (y_max - y_min) / 640
            
            labels_list.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
            
        # Save output image
        img_filename = os.path.join(OUTPUT_DIR, split, "images", f"synth_{idx}.jpg")
        composite.save(img_filename, "JPEG")
        
        # Save output labels
        lbl_filename = os.path.join(OUTPUT_DIR, split, "labels", f"synth_{idx}.txt")
        with open(lbl_filename, "w") as lf:
            lf.write("\n".join(labels_list) + "\n")

# 5. Generate Master Data Mapping Configuration
yaml_str = f"""path: {OUTPUT_DIR}
train: train/images
val: val/images
test: test/images
names:
  0: plastic_pet_hdpe
  1: paper_cardboard
  2: metal_aluminum_steel
  3: glass_bottles_jars
  4: organic_food_waste
  5: ewaste_hazardous
"""

with open(os.path.join(OUTPUT_DIR, "data.yaml"), "w") as yf:
    yf.write(yaml_str)

print(f"[SUCCESS] Synthetic 6-Class Multi-Object Dataset successfully compiled to: {OUTPUT_DIR}")
