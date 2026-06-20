from ultralytics import YOLO
import os
import sys

# 1. Automatic Environment Detection
if os.path.exists("/content"):
    # Google Colab Environment
    print("[ENV] Detected Google Colab Environment.")
    yaml_config = "/content/drive/MyDrive/VISION_BIN_PROJECT/vision_bin_public_dataset/data.yaml"
    project_dir = "/content/drive/MyDrive/VISION_BIN_PROJECT/runs"
    device_arg = 0  # GPU device 0 in Colab
    workers_arg = 2
else:
    # Local Windows Environment
    print("[ENV] Detected Local Windows Environment.")
    yaml_config = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/vision_bin_public_dataset/data.yaml"
    project_dir = "C:/Users/kumku/.gemini/antigravity/scratch/drishti_cps_proposal/VISION-BIN/runs"
    device_arg = 'cpu'  # Default to CPU for local checks unless CUDA is configured
    workers_arg = 0

# Check if data.yaml exists
if not os.path.exists(yaml_config):
    print(f"[ERROR] Config file not found at: {yaml_config}")
    print("[HELP] Please run harmonize_dataset.py first to compile the dataset.")
    sys.exit(1)

# Check for validation/test run arg
epochs_val = 30
if "--test-run" in sys.argv:
    print("[TEST] Running 1-epoch validation test run...")
    epochs_val = 1

recovery_weights = os.path.join(project_dir, "vision_bin_baseline_prod", "weights", "last.pt")

# Check if a late-stage execution save file exists to handle sudden network throttling/disconnections
if os.path.exists(recovery_weights) and "--test-run" not in sys.argv:
    print("[RECOVERY] Located previous run weights. Resuming model training...")
    model = YOLO(recovery_weights)
    model.train(resume=True)
else:
    print(f"[START] Triggering fresh {epochs_val}-epoch training baseline...")
    # Load light YOLO11 nano model for fast deployment
    model = YOLO('yolo11n.pt')
    
    # Train with advanced augmentations to handle multi-object overlays and cluttered backgrounds
    model.train(
        data=yaml_config, 
        epochs=epochs_val, 
        imgsz=640, 
        batch=16 if device_arg == 'cpu' else 32, 
        device=device_arg, 
        workers=workers_arg, 
        save=True,
        project=project_dir, 
        name="vision_bin_baseline_prod",
        # Augmentations for cluttered backgrounds & overlapping multiple objects
        mosaic=1.0,     # Combines 4 training images to simulate complex multi-object scenes
        mixup=0.15,     # Blends images to help identify overlapping items
        degrees=15.0,   # Random rotations to handle objects at arbitrary angles
        flipud=0.5,     # Vertical flips
        fliplr=0.5     # Horizontal flips
    )
print("[COMPLETE] Core production weights successfully compiled.")
