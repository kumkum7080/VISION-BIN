class SensorFusionEngine:
    def __init__(self):
        self.class_names = {
            0: "plastic_pet_hdpe",
            1: "paper_cardboard",
            2: "metal_aluminum_steel",
            3: "glass_bottles_jars",
            4: "organic_food_waste",
            5: "ewaste_hazardous"
        }
        
    def fuse_sensors(self, predicted_class_id, confidence, inductive_detected, capacitive_detected, moisture_level, weight_grams):
        """
        Fuses visual prediction with physical sensor parameters to produce a final class decision.
        
        Args:
            predicted_class_id (int): Class predicted by YOLOv11 (0-5)
            confidence (float): Classification confidence (0.0 to 1.0)
            inductive_detected (bool): Signal from LJ12 sensor (True = metal present)
            capacitive_detected (bool): Signal from LJC18 sensor (True = dense solid present)
            moisture_level (float): Normalized moisture level (0.0 = dry, 1.0 = wet)
            weight_grams (float): Weight of the item measured by the load cell
            
        Returns:
            dict: Final classification details containing:
                  - class_id (int)
                  - name (str)
                  - override_triggered (bool)
                  - override_reason (str)
                  - confidence (float)
        """
        final_class_id = predicted_class_id
        override_triggered = False
        override_reason = "No override - visual prediction accepted."
        final_confidence = confidence
        
        # Rule 1: Inductive proximity sensor override (Metal Detection)
        # Inductive sensors only trigger on conductive metals. If triggered, it is metal.
        if inductive_detected:
            if predicted_class_id != 2:
                final_class_id = 2
                override_triggered = True
                override_reason = f"Inductive sensor active. Overrode visual prediction '{self.class_names[predicted_class_id]}' to Metal."
                final_confidence = 1.0  # Absolute certainty
            return self._build_result(final_class_id, override_triggered, override_reason, final_confidence)
            
        # Rule 2: Moisture sensor override (Organic / Wet Waste)
        # High moisture items (e.g. food scraps, wet cardboard) are routed to Organic to prevent dry bin contamination.
        if moisture_level > 0.6:
            if predicted_class_id != 4:
                final_class_id = 4
                override_triggered = True
                override_reason = f"High moisture level ({moisture_level:.2f}) detected. Overrode visual prediction to Organic."
                final_confidence = max(confidence, 0.9)
            return self._build_result(final_class_id, override_triggered, override_reason, final_confidence)

        # Rule 3: Weight and Capacitive override for Glass vs Plastic
        # If camera predicts Glass (heavy) but it is extremely light, it is likely plastic wrap/bottle.
        if predicted_class_id == 3:  # Glass
            if weight_grams < 40.0:
                final_class_id = 0  # Plastic
                override_triggered = True
                override_reason = f"Visual prediction was Glass, but weight is extremely light ({weight_grams:.1f}g). Overrode to Plastic."
                final_confidence = 0.85
                return self._build_result(final_class_id, override_triggered, override_reason, final_confidence)
                
        # If camera predicts Plastic (light) but weight is heavy and capacitive is active, it is likely glass.
        if predicted_class_id == 0:  # Plastic
            if weight_grams > 200.0 and capacitive_detected:
                final_class_id = 3  # Glass
                override_triggered = True
                override_reason = f"Visual prediction was Plastic, but weight is heavy ({weight_grams:.1f}g) and capacitive sensor is active. Overrode to Glass."
                final_confidence = 0.85
                return self._build_result(final_class_id, override_triggered, override_reason, final_confidence)

        # Rule 4: Dry Paper / Cardboard vs Plastic
        # Paper has very low capacitive readings compared to dense plastics.
        if predicted_class_id == 1:  # Paper
            if weight_grams > 150.0 and capacitive_detected:
                # Heavy and capacitive dense item, likely glass or plastic container
                final_class_id = 3  # Glass
                override_triggered = True
                override_reason = f"Visual prediction was Paper, but weight is heavy ({weight_grams:.1f}g) and capacitive sensor is active. Overrode to Glass."
                final_confidence = 0.75
                return self._build_result(final_class_id, override_triggered, override_reason, final_confidence)

        # Rule 5: Visual prediction checks for E-waste
        # If camera has high confidence of E-waste, we route it directly.
        
        return self._build_result(final_class_id, override_triggered, override_reason, final_confidence)
        
    def _build_result(self, class_id, override_triggered, override_reason, confidence):
        return {
            "class_id": class_id,
            "name": self.class_names[class_id],
            "override_triggered": override_triggered,
            "override_reason": override_reason,
            "confidence": confidence
        }

if __name__ == "__main__":
    # Quick self-test
    engine = SensorFusionEngine()
    
    # Test case: Coke can incorrectly classified as plastic bottle
    result = engine.fuse_sensors(
        predicted_class_id=0, # Plastic
        confidence=0.65,
        inductive_detected=True, # Metal sensor active!
        capacitive_detected=True,
        moisture_level=0.1,
        weight_grams=15.0
    )
    print("Test Case (Coke Can):")
    print(f"  Final Decision: {result['name']} (Class {result['class_id']})")
    print(f"  Override? {result['override_triggered']} - {result['override_reason']}")
