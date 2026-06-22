import subprocess
import os

API_KEY = "TY1Yt0QRbvzQtd9lydtI"
PROJECT_ID = "vision-bin-127wk"
RAW_DIR = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/custom_dataset_subset"

subfolders = [
    ("1_paper_cardboard", "1_paper_cardboard"),
    ("2_metal_aluminum_steel", "2_metal_aluminum_steel"),
    ("3_glass_bottles_jars", "3_glass_bottles_jars"),
    ("4_organic_food_waste", "4_organic_food_waste"),
    ("5_ewaste_hazardous", "5_ewaste_hazardous")
]

# Set environment variable
os.environ["ROBOFLOW_API_KEY"] = API_KEY

cli_path = r"C:\Users\kumku\AppData\Local\Programs\Python\Python312\Scripts\roboflow.exe"

for folder, tag in subfolders:
    folder_path = os.path.join(RAW_DIR, folder)
    print(f"\n=========================================")
    print(f"[ZIP UPLOAD] Starting upload for {folder} with tag {tag}")
    print(f"=========================================")
    
    cmd = [
        cli_path, "image", "upload",
        folder_path,
        "-p", PROJECT_ID,
        "-t", tag,
        "--zip-upload"
    ]
    
    # Run the command and stream output
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    for line in process.stdout:
        print(line, end="")
        
    process.wait()
    if process.returncode == 0:
        print(f"[ZIP UPLOAD] Successfully completed upload for {folder}")
    else:
        print(f"[ZIP UPLOAD] Failed upload for {folder} with return code {process.returncode}")

print("\nAll remaining zip uploads finished!")
