import os
import random
import shutil

SOURCE_DIR = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/custom_dataset"
SUBSET_DIR = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/custom_dataset_subset"

subfolders = [
    "0_plastic_pet_hdpe",
    "1_paper_cardboard",
    "2_metal_aluminum_steel",
    "3_glass_bottles_jars",
    "4_organic_food_waste",
    "5_ewaste_hazardous"
]

print("=== CREATING 3,000-IMAGE SUBSET ===")
# Ensure subset directory exists
os.makedirs(SUBSET_DIR, exist_ok=True)

for folder in subfolders:
    src_path = os.path.join(SOURCE_DIR, folder)
    dest_path = os.path.join(SUBSET_DIR, folder)
    os.makedirs(dest_path, exist_ok=True)
    
    if os.path.exists(src_path):
        # List all images
        files = [f for f in os.listdir(src_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        # Shuffle and select 1000
        random.shuffle(files)
        selected_files = files[:1000]
        
        print(f"Copying {len(selected_files)} images for {folder}...")
        for filename in selected_files:
            shutil.copy2(
                os.path.join(src_path, filename),
                os.path.join(dest_path, filename)
            )
            
        # Add .gitkeep
        with open(os.path.join(dest_path, ".gitkeep"), "w") as k:
            k.write("")
    else:
        print(f"[Warning] Folder {folder} not found!")

# Zip the subset
print("\nCompressing subset into custom_dataset_subset.zip...")
shutil.make_archive(SUBSET_DIR, 'zip', SUBSET_DIR)
print("[SUCCESS] custom_dataset_subset.zip created successfully!")
