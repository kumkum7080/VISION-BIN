import time
import os
import sys

# Import local CPS components
from sensor_fusion_engine import SensorFusionEngine
from hardware_controllers import HardwareController

# Try loading YOLO from ultralytics
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

class MockYOLOModel:
    """Mock object detection model used in PC testing mode when YOLO is not installed."""
    def __init__(self):
        print("[PIPELINE] Initialized Mock YOLO Model.")
        
    def predict(self, source, verbose=False):
        """Simulates YOLO predictions based on the input filename or defaults to class 0."""
        # Clean path formatting
        filename = os.path.basename(source).lower()
        
        # Hardcoded classes mapping to names:
        # 0: plastic, 1: paper, 2: metal, 3: glass, 4: organic, 5: e-waste
        class_id = 0
        confidence = 0.85
        
        if "can" in filename or "metal" in filename:
            class_id = 2
        elif "paper" in filename or "cardboard" in filename or "box" in filename:
            class_id = 1
        elif "glass" in filename or "jar" in filename or "bottle" in filename and "plastic" not in filename:
            class_id = 3
        elif "banana" in filename or "apple" in filename or "peel" in filename or "food" in filename:
            class_id = 4
        elif "keyboard" in filename or "phone" in filename or "battery" in filename:
            class_id = 5
        elif "bottle" in filename:
            class_id = 0 # Plastic bottle
            
        class MockResult:
            def __init__(self, cid, conf):
                self.probs = None
                self.boxes = self # Mock box interface
                self.cls = [cid]
                self.conf = [conf]
                
        return [MockResult(class_id, confidence)]

class SortingPipeline:
    def __init__(self, weights_path=None, use_mock_hw=None):
        self.fusion_engine = SensorFusionEngine()
        self.hw = HardwareController(use_mock=use_mock_hw)
        
        # Load YOLO model
        self.yolo_model = None
        if weights_path and os.path.exists(weights_path) and ULTRALYTICS_AVAILABLE:
            try:
                self.yolo_model = YOLO(weights_path)
                print(f"[PIPELINE] Loaded active YOLOv11 weights from: {weights_path}")
            except Exception as e:
                print(f"[PIPELINE] Error loading weights: {e}. Falling back to mock vision.")
                
        if self.yolo_model is None:
            self.yolo_model = MockYOLOModel()
            
    def process_waste_item(self, image_source):
        """
        Runs the complete Cyber-Physical waste segregation transaction.
        
        1. Lock safety shutters.
        2. Snapshot and run AI image classification.
        3. Read physical proximity, moisture, and weight data.
        4. Fuse multi-modal inputs.
        5. Stepper rotate Teflon chute.
        6. Release trapdoor servo.
        7. Home stepper and unlock shutters.
        """
        print("\n=== STARTING WASTE SEGREGATION CYCLE ===")
        print(f"[PIPELINE] Processing item. Visual source: {image_source}")
        
        # 1. Close entry shutter gate servo
        self.hw.operate_gate(open_gate=False)
        time.sleep(0.5)
        
        # 2. Read physical sensors
        print("[PIPELINE] Reading physical sensors...")
        inductive = self.hw.read_inductive()
        capacitive = self.hw.read_capacitive()
        moisture = self.hw.read_moisture()
        weight = self.hw.read_weight()
        
        print(f"  LJ12 Inductive Metal sensor: {inductive}")
        print(f"  LJC18 Capacitive Proximity:  {capacitive}")
        print(f"  FC-28 Soil Moisture Level:   {moisture:.2f}")
        print(f"  HX711 Weight Scale:          {weight:.1f} grams")
        
        # 3. Snapshot & Run YOLO AI classification
        print("[PIPELINE] Running YOLOv11 Object Detection inference...")
        results = self.yolo_model.predict(image_source, verbose=False)
        
        # Retrieve top prediction class & confidence
        if results and len(results[0].boxes.cls) > 0:
            predicted_class_id = int(results[0].boxes.cls[0])
            confidence = float(results[0].boxes.conf[0])
        else:
            predicted_class_id = 0  # Default to plastic
            confidence = 0.50
            
        print(f"  AI Visual Class Prediction: {self.fusion_engine.class_names[predicted_class_id]} (Class {predicted_class_id})")
        print(f"  AI Visual Class Confidence: {confidence:.2f}")
        
        # 4. Run Multi-Sensor Fusion Decision Engine
        print("[PIPELINE] Executing Sensor Fusion Engine...")
        fusion_result = self.fusion_engine.fuse_sensors(
            predicted_class_id=predicted_class_id,
            confidence=confidence,
            inductive_detected=inductive,
            capacitive_detected=capacitive,
            moisture_level=moisture,
            weight_grams=weight
        )
        
        final_id = fusion_result["class_id"]
        final_name = fusion_result["name"]
        print(f"  FUSION RESULT: {final_name} (Class {final_id})")
        if fusion_result["override_triggered"]:
            print(f"  ⚠️ OVERRIDE TRIGGERED: {fusion_result['override_reason']}")
        else:
            print("  Decision match: AI visual prediction confirmed by sensors.")
            
        # 5. Rotate Teflon chute stepper motor to the target bin compartment (60 deg segments)
        print(f"[PIPELINE] Aligning physical chute to Bin {final_id} ({final_name})...")
        self.hw.rotate_to_bin(final_id)
        time.sleep(0.5)
        
        # 6. Open the trapdoor drop tray servo
        self.hw.operate_drop_tray(open_drop=True)
        print("[PIPELINE] Waste item dropped down the Teflon chute.")
        time.sleep(2.0)  # Wait for item to slide down
        
        # 7. Close trapdoor drop tray servo
        self.hw.operate_drop_tray(open_drop=False)
        time.sleep(0.5)
        
        # 8. Reset stepper to home (0 steps) to prevent wire twisting
        self.hw.reset_to_home()
        
        # 9. Open the entry shutter gate servo for next deposit
        self.hw.operate_gate(open_gate=True)
        print("=== CYCLE COMPLETED SUCCESSFULLY ===\n")
        
        return fusion_result

    def run_polling_loop(self):
        """Standard polling loop that runs continuously, waiting for infrared deposit triggers."""
        print("[PIPELINE] System initialized. Entering polling loop. Waiting for waste deposit...")
        try:
            while True:
                if self.hw.check_entry_trigger():
                    print("[PIPELINE] Deposit detected! Starting sorting sequence.")
                    # In real HW, this would take a photo from webcam to 'capture.jpg'
                    self.process_waste_item("capture.jpg")
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.hw.cleanup()
            print("[PIPELINE] Shutting down.")

if __name__ == "__main__":
    # Test execution in mock environment
    pipeline = SortingPipeline(use_mock_hw=True)
    
    # Simulate a Pepsi metal can trigger
    pipeline.hw.set_mock_sensor_values(
        inductive=True,
        capacitive=True,
        moisture=0.1,
        weight=15.0,
        entry=True
    )
    pipeline.process_waste_item("pepsi_can.jpg")
