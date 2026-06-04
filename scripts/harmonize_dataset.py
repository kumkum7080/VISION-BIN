import os
import glob
import shutil
import random
import yaml
import cv2
import numpy as np

# 1. Path Architecture Definitions
OUTPUT_DIR = "/content/vision_bin_public_dataset"
DRIVE_PROJECT_PATH = "/content/drive/MyDrive/VISION_BIN_PROJECT"
DRIVE_DATASET_PATH = os.path.join(DRIVE_PROJECT_PATH, "vision_bin_public_dataset")
RAW_TRASHNET_DIR = "/content/raw_data/trashnet"

# Clear old dataset compilations
for path in [OUTPUT_DIR, DRIVE_DATASET_PATH]:
    if os.path.exists(path):
        shutil.rmtree(path)

# Create train/val/test splits
SPLITS = ["train", "val", "test"]
for split in SPLITS:
    for sub in ["images", "labels"]:
        os.makedirs(os.path.join(OUTPUT_DIR, split, sub), exist_ok=True)

# 2. Ingest Public Dry Waste Categories
TRASHNET_MAP = {"plastic": 0, "paper": 1, "cardboard": 1, "metal": 2, "glass": 3}

trashnet_counter = 0
for folder_name, target_class_id in TRASHNET_MAP.items():
    source_folder = os.path.join(RAW_TRASHNET_DIR, folder_name)
    if not os.path.exists(source_folder): continue
    for img_path in glob.glob(os.path.join(source_folder, "*.*")):
        # 80/10/10 Split Mapping
        split = "train" if random.random() < 0.80 else ("val" if random.random() < 0.90 else "test")
        ext = os.path.splitext(img_path)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']: continue
        
        base = f"trashnet_{trashnet_counter}"
        shutil.copy(img_path, os.path.join(OUTPUT_DIR, split, "images", f"{base}{ext}"))
        
        # Inject standard uniform centered bounding box configurations
        with open(os.path.join(OUTPUT_DIR, split, "labels", f"{base}.txt"), "w") as lf:
            lf.write(f"{target_class_id} 0.500000 0.500000 0.850000 0.850000\n")
        trashnet_counter += 1

# 3. Inject Structural Empty Canvas Placeholders for Organic and E-Waste
blank_canvas = np.zeros((640, 640, 3), dtype=np.uint8)
for split in SPLITS:
    cv2.imwrite(os.path.join(OUTPUT_DIR, split, "images", "placeholder_class_4_5.jpg"), blank_canvas)
    with open(os.path.join(OUTPUT_DIR, split, "labels", "placeholder_class_4_5.txt"), "w") as f:
        f.write("4 0.500000 0.500000 0.010000 0.010000\n")
        f.write("5 0.500000 0.500000 0.010000 0.010000\n")

# 4. Generate Master Data Mapping Configuration
yaml_payload = {
    "path": DRIVE_DATASET_PATH,
    "train": "train/images", "val": "val/images", "test": "test/images",
    "names": {
        0: "plastic_pet_hdpe", 
        1: "paper_cardboard", 
        2: "metal_aluminum_steel", 
        3: "glass_bottles_jars", 
        4: "organic_food_waste", 
        5: "ewaste_hazardous"
    }
}
with open(os.path.join(OUTPUT_DIR, "data.yaml"), "w") as yf:
    yaml.dump(yaml_payload, yf, default_flow_style=False, sort_keys=False)

# Sync execution files up to Google Drive
shutil.copytree(OUTPUT_DIR, DRIVE_DATASET_PATH)
print("[SUCCESS] Production dataset structures built and synced to Google Drive.")
