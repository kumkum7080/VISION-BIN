import os
from roboflow import Roboflow

API_KEY = "TY1Yt0QRbvzQtd9lydtI"
WORKSPACE_ID = "kumkums-workspace-wfgjm"
PROJECT_NAME = "vision-bin-127wk"

try:
    print("Initializing Roboflow...")
    rf = Roboflow(api_key=API_KEY)
    workspace = rf.workspace(WORKSPACE_ID)
    project = workspace.project(PROJECT_NAME)
    
    # Locate a sample image in our subset
    sample_img = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/custom_dataset_subset/0_plastic_pet_hdpe/raw_waste_0_1.jpg"
    if not os.path.exists(sample_img):
        # Fallback to any file in that directory
        folder = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/custom_dataset_subset/0_plastic_pet_hdpe"
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if files:
            sample_img = os.path.join(folder, files[0])
            
    print(f"Uploading sample image: {sample_img}")
    res = project.upload(
        image_path=sample_img,
        tag_names=["test_tag"],
        split="train"
    )
    print(f"[SUCCESS] Upload response: {res}")
except Exception as e:
    print(f"[ERROR] Upload failed: {e}")
