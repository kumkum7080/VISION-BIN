import os

base_dirs = [
    "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/custom_dataset",
    "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/custom_dataset_subset"
]

folders_prefixes = {
    "0_plastic_pet_hdpe": "plastic_pet_hdpe",
    "1_paper_cardboard": "paper_cardboard",
    "2_metal_aluminum_steel": "metal_aluminum_steel",
    "3_glass_bottles_jars": "glass_bottles_jars",
    "4_organic_food_waste": "organic_food_waste",
    "5_ewaste_hazardous": "ewaste_hazardous"
}

image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif')

for base_dir in base_dirs:
    if not os.path.exists(base_dir):
        print(f"[RENAME] Directory not found: {base_dir}")
        continue
        
    print(f"\n[RENAME] Scanning base directory: {base_dir}")
    for folder, prefix in folders_prefixes.items():
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            print(f"  Folder not found: {folder_path}")
            continue
            
        # Get all image files in the directory
        files = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith(image_extensions)
        ]
        
        # Sort files to ensure deterministic/stable ordering
        files.sort()
        
        print(f"  Renaming {len(files)} images in '{folder}' with prefix '{prefix}'...")
        
        # First pass: rename to a temporary name to avoid collisions
        temp_renames = []
        for idx, filename in enumerate(files, start=1):
            src_path = os.path.join(folder_path, filename)
            ext = os.path.splitext(filename)[1].lower()
            temp_name = f"__temp_{prefix}_{idx:05d}{ext}"
            temp_path = os.path.join(folder_path, temp_name)
            
            try:
                os.rename(src_path, temp_path)
                temp_renames.append((temp_path, f"{prefix}{idx:05d}{ext}"))
            except Exception as e:
                print(f"    Error renaming {filename} to temporary name: {e}")
                
        # Second pass: rename from temporary to final name
        success_count = 0
        for temp_path, final_name in temp_renames:
            final_path = os.path.join(os.path.dirname(temp_path), final_name)
            try:
                os.rename(temp_path, final_path)
                success_count += 1
            except Exception as e:
                print(f"    Error renaming {os.path.basename(temp_path)} to {final_name}: {e}")
                
        print(f"  Successfully renamed {success_count}/{len(files)} images.")

print("\n[RENAME] Completed renaming all images!")
