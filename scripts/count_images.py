import os

RAW_DIR = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/custom_dataset"
subfolders = [
    "0_plastic_pet_hdpe",
    "1_paper_cardboard",
    "2_metal_aluminum_steel",
    "3_glass_bottles_jars",
    "4_organic_food_waste",
    "5_ewaste_hazardous"
]

print("=== IMAGE COUNTS IN CUSTOM DATASET ===")
total = 0
for folder in subfolders:
    path = os.path.join(RAW_DIR, folder)
    if os.path.exists(path):
        files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"Class {folder}: {len(files)} images")
        total += len(files)
    else:
        print(f"Class {folder}: Directory not found!")
print(f"Total Images: {total}")
print("======================================")
