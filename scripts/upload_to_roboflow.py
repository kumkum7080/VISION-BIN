import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from roboflow import Roboflow

import time
import random

API_KEY = "TY1Yt0QRbvzQtd9lydtI"
WORKSPACE_ID = "kumkums-workspace-wfgjm"
PROJECT_NAME = "vision-bin-127wk"

# Initialize Roboflow Client
rf = Roboflow(api_key=API_KEY)
workspace = rf.workspace(WORKSPACE_ID)

# Locate or create the project
try:
    project = workspace.project(PROJECT_NAME)
    print(f"[ROBOFLOW] Located existing project: {PROJECT_NAME}")
except Exception:
    print(f"[ROBOFLOW] Project '{PROJECT_NAME}' not found. Creating a new one...")
    project = workspace.create_project(
        project_name=PROJECT_NAME,
        project_type="object-detection",
        project_license="MIT",
        annotation="waste"
    )
    print(f"[ROBOFLOW] Created project: {project.id}")

RAW_DIR = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/custom_dataset_subset"
subfolders = [
    ("0_plastic_pet_hdpe", "0_plastic_pet_hdpe"),
    ("1_paper_cardboard", "1_paper_cardboard"),
    ("2_metal_aluminum_steel", "2_metal_aluminum_steel"),
    ("3_glass_bottles_jars", "3_glass_bottles_jars"),
    ("4_organic_food_waste", "4_organic_food_waste"),
    ("5_ewaste_hazardous", "5_ewaste_hazardous")
]

# Compile upload queue
upload_queue = []
for folder, tag in subfolders:
    folder_path = os.path.join(RAW_DIR, folder)
    if os.path.exists(folder_path):
        files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        for file in files:
            upload_queue.append((file, tag))

print(f"\n[ROBOFLOW] Found {len(upload_queue)} images in subset queue.")

# Upload function for a single file
def upload_single_file(file_info):
    file_path, tag = file_info
    filename = os.path.basename(file_path)
    try:
        # Rate-limiting: add a tiny delay to avoid over-whelming the Roboflow API
        time.sleep(random.uniform(0.1, 0.4))
        project.upload(
            image_path=file_path,
            tag_names=[tag],
            split="train",
            num_retry_uploads=5
        )
        return True, filename
    except Exception as e:
        return False, f"{filename}: {e}"

# Concurrent execution using ThreadPoolExecutor
print("[ROBOFLOW] Starting parallel upload with 5 threads...")
success_count = 0
failed_count = 0

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(upload_single_file, item): item for item in upload_queue}
    
    for idx, future in enumerate(as_completed(futures)):
        success, info = future.result()
        if success:
            success_count += 1
        else:
            failed_count += 1
            print(f"  [Failed] {info}")
            
        if (idx + 1) % 100 == 0:
            print(f"  Progress: {idx + 1}/{len(upload_queue)} uploaded ({success_count} success, {failed_count} failed)")

print("\n=== UPLOAD SUMMARY ===")
print(f"Successfully Uploaded: {success_count}")
print(f"Failed Uploads: {failed_count}")
print("=======================")
