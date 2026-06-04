from ultralytics import YOLO
import os

drive_yaml_config = "/content/drive/MyDrive/VISION_BIN_PROJECT/vision_bin_public_dataset/data.yaml"
recovery_weights = "/content/drive/MyDrive/VISION_BIN_PROJECT/runs/vision_bin_baseline_prod/weights/last.pt"

# Check if a late-stage execution save file exists to handle sudden network throttling
if os.path.exists(recovery_weights):
    print("[RECOVERY] Located previous run. Resuming model compilation...")
    model = YOLO(recovery_weights)
    model.train(resume=True)
else:
    print("[START] Triggering fresh 30-epoch training baseline on NVIDIA T4 GPU...")
    model = YOLO('yolo11n.pt')
    model.train(
        data=drive_yaml_config, 
        epochs=30, 
        imgsz=640, 
        batch=32, 
        device=0, 
        workers=2, 
        save=True,
        project="/content/drive/MyDrive/VISION_BIN_PROJECT/runs", 
        name="vision_bin_baseline_prod"
    )
print("[COMPLETE] Core production weights successfully compiled to Google Drive.")
