import os
import sys

# Import local CPS components
from inference_pipeline import SortingPipeline

def run_integration_test():
    print("=====================================================================")
    print("             VISION BIN MULTI-SENSOR PIPELINE TESTING                ")
    print("=====================================================================")
    
    # Initialize the sorting pipeline in mock hardware mode
    pipeline = SortingPipeline(use_mock_hw=True)
    
    # Define the 6 test cases representing standard waste categories and overrides
    test_cases = [
        {
            "name": "Coca-Cola Aluminum Can",
            "image": "crumpled_cup_reflective.jpg",  # No keyword, predicts Plastic (0)
            "sensors": {
                "inductive": True,         # Metal detected!
                "capacitive": True,
                "moisture": 0.05,          # Dry
                "weight": 14.5             # Lightweight
            },
            "expected_class": 2,           # Metal (Overridden from Plastic)
            "desc": "Tests if inductive proximity sensor overrides an incorrect/low-conf visual prediction of Plastic to Metal."
        },
        {
            "name": "Organic Banana Peel",
            "image": "dry_cardboard_box_wet.jpg",    # Contains 'box', predicts Paper (1)
            "sensors": {
                "inductive": False,
                "capacitive": True,
                "moisture": 0.85,          # High moisture!
                "weight": 85.0
            },
            "expected_class": 4,           # Organic (Overridden from Paper due to moisture)
            "desc": "Tests if high moisture level triggers organic sorting even if visual prediction says Paper."
        },
        {
            "name": "HDPE Milk Jug",
            "image": "plastic_milk_jug.jpg",         # Contains 'plastic', predicts Plastic (0)
            "sensors": {
                "inductive": False,
                "capacitive": True,         # Solid plastic detected
                "moisture": 0.1,
                "weight": 45.0             # Light
            },
            "expected_class": 0,           # Plastic
            "desc": "Tests standard recyclable plastic sorting based on visual and low weight."
        },
        {
            "name": "Heavy Glass Jar",
            "image": "plastic_bottle_heavy.jpg",     # Contains 'bottle', predicts Plastic (0)
            "sensors": {
                "inductive": False,
                "capacitive": True,
                "moisture": 0.1,
                "weight": 350.0            # Heavy solid! (Glass override)
            },
            "expected_class": 3,           # Glass (Overridden from Plastic due to heavy weight + capacitive)
            "desc": "Tests glass sorting by overriding a Plastic visual prediction when weight is heavy and capacitive is active."
        },
        {
            "name": "Crumpled Newspaper",
            "image": "folded_newspaper_paper.jpg",   # Contains 'paper', predicts Paper (1)
            "sensors": {
                "inductive": False,
                "capacitive": False,        # Low density/air
                "moisture": 0.05,
                "weight": 18.0
            },
            "expected_class": 1,           # Paper
            "desc": "Tests paper sorting based on visual and low capacitance/moisture."
        },
        {
            "name": "AA Alkaline Battery",
            "image": "battery_aa.jpg",               # Contains 'battery', predicts E-waste (5)
            "sensors": {
                "inductive": False,
                "capacitive": True,
                "moisture": 0.0,
                "weight": 23.0
            },
            "expected_class": 5,           # E-waste
            "desc": "Tests hazardous e-waste sorting based on visual class mapping."
        }
    ]
    
    passed_count = 0
    results_summary = []
    
    for idx, tc in enumerate(test_cases):
        print(f"\n--- TEST CASE {idx+1}: {tc['name']} ---")
        print(f"Goal: {tc['desc']}")
        
        # Set mock sensor states
        pipeline.hw.set_mock_sensor_values(
            inductive=tc["sensors"]["inductive"],
            capacitive=tc["sensors"]["capacitive"],
            moisture=tc["sensors"]["moisture"],
            weight=tc["sensors"]["weight"],
            entry=True
        )
        
        # Process the sorting transaction
        res = pipeline.process_waste_item(tc["image"])
        
        # Verify the results
        final_id = res["class_id"]
        expected_id = tc["expected_class"]
        status = "PASSED" if final_id == expected_id else "FAILED"
        
        if status == "PASSED":
            passed_count += 1
            
        results_summary.append({
            "idx": idx+1,
            "name": tc["name"],
            "prediction": pipeline.fusion_engine.class_names[expected_id],
            "decision": res["name"],
            "override": "Yes" if res["override_triggered"] else "No",
            "status": status
        })
        
    # Print formatted results table
    print("\n" + "="*80)
    print("                         INTEGRATION TESTS SUMMARY                          ")
    print("="*80)
    print(f"{'ID':<3} | {'Test Scenario':<25} | {'Visual Pred':<15} | {'Decision':<15} | {'Override':<8} | {'Status':<6}")
    print("-"*80)
    for r in results_summary:
        print(f"{r['idx']:<3} | {r['name']:<25} | {r['prediction']:<15} | {r['decision']:<15} | {r['override']:<8} | {r['status']:<6}")
    print("="*80)
    
    print(f"\nResult: {passed_count}/{len(test_cases)} tests passed.")
    if passed_count == len(test_cases):
        print("ALL TESTS PASSED! The Cyber-Physical sensor fusion stack is verified and ready.")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED. Please review the fusion thresholds or motor step settings.")
        sys.exit(1)

if __name__ == "__main__":
    run_integration_test()
