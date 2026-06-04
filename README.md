# VISION-BIN: AI-Powered Smart Waste Segregation System
> **Indian Institute of Technology Indore (IIT Indore)**
> **Core Developers:** ce240004028@iiti.ac.in | ce240004033@iiti.ac.in  
> *A hardware-optimized, edge-deployable non-rigid object detection framework designed for automated mechanical sorting bins.*

---

## 1. The Global Waste Crisis & Project Motivation
Traditional public waste disposal methods suffer from structural inefficiencies that compromise downstream recycling. VISION-BIN resolves these bottlenecks by targeting three specific challenges:

1. **The Contamination Crisis:** Standard bins rely entirely on user discretion. "Wish-cycling" introduces food residue and mismatched items into recycling channels, cross-contaminating and ruining up to 40% of potentially recyclable material.
2. **The "Deformation" Gap in Existing Industrial Automation:** High-end commercial automated solutions (such as the $5,000 industrial Bin-e system) fail in real-world public domains because their vision networks are trained heavily on "ideal", pristine geometric shapes. VISION-BIN implements **Non-Rigid Object Detection** to accurately identify items when they are crumpled, crushed, twisted, or partially deformed.
3. **The Multi-Class Contamination (Liquid) Problem:** Standard computer vision cannot deduce volume or weight. Bins frequently accept a half-full beverage bottle as "Plastic," which subsequently leaks and destroys dry fractions like "Paper." VISION-BIN's system architecture lays the foundation for multi-modal validation (fusing vision inference with weight sensors) to halt sorting if an item is contaminated.

---

## 2. Strict 6-Class Taxonomy & Network Pruning
To prevent overlapping bounding boxes and latency issues on edge computing hardware, we performed network pruning to wipe out YOLO's default 80-class COCO vocabulary (completely disabling irrelevant detections like `person`, `car`, or `dog`). The system forces all classification onto a strict, municipal-grade **6-door classification matrix**:

* **Class 0: `plastic_pet_hdpe`** — Focuses on high-economic-value consumer beverage containers (e.g., Bisleri, Aquafina, soft drink bottles, milk jugs). Trained specifically to recognize non-rigid variations so crushed containers are successfully caught.
* **Class 1: `paper_cardboard`** — Exam answer sheets, cardboard shipping boxes, newspapers, and shredded office scrap.
* **Class 2: `metal_aluminum_steel`** — Soft drink cans (Thums Up, Coca-Cola), steel tiffin containers, and aluminum foil wraps.
* **Class 3: `glass_bottles_jars`** — Commercial glass bottles and jars (Limca, Gold Spot, juice containers).
* **Class 4: `organic_food_waste`** — Wet cafeteria scraps, fruit rinds, banana peels, apple cores, tea leaves, and spilled food. Segregating this is critical to keeping the dry recycling classes uncontaminated.
* **Class 5: `ewaste_hazardous`** — Discarded lab wires, dead AA/lithium batteries, old charging cables, copper coils, and circuit board segments.

---

## 3. End-to-End System Mechanical Pipeline
The physical hardware and AI software components interface in a continuous edge-computing loop:

```text
[ USER DROPS WASTE ]
         │
         ▼
 ┌──────────────┐
 │ 1. INTAKE    │ ──> User drops an unsorted item into a single universal chute.
 │    CHUTE     │
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │ 2. OVERHEAD  │ ──> A camera sensor mounted inside captures a high-resolution 
 │    CAMERA    │     640x640 frame under controlled internal bin lighting.
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │ 3. EDGE AI   │ ──> Microcontroller (Raspberry Pi / NVIDIA Jetson) runs local 
 │    BRAIN     │     inference on the frame using our optimized 'best.pt' weights.
 └──────┬───────┘     Extracts Target Class ID if Confidence > 50%.
        │
        ▼
 ┌──────────────┐
 │ 4. SIGNAL    │ ──> Maps the Class ID to a specific Pulse Width Modulation 
 │    MAPPING   │     (PWM) angle command (e.g., Class 4 Organic ➔ 180°).
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │ 5. SERVO     │ ──> A heavy-duty electric servo motor spins a mechanical,
 │    ACTUATION │     rotating distribution flap to the matching angle marker.
 └──────┬───────┘
        │
        ▼
 [ PHYSICAL SEPARATION INTO THE SEGREGATED INTERNAL BINS ]
 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
 │   Slot 0:    │ │   Slot 1:    │ │   Slot 2:    │ │   Slot 3:    │ │   Slot 4:    │ │   Slot 5:    │
 │   Plastic    │ │    Paper     │ │    Metal     │ │    Glass     │ │   ORGANIC    │ │   E-Waste    │
 └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘

```

##  4. Phase 1 & 2 Production Performance Baseline

The baseline machine learning brain was trained on an NVIDIA Tesla T4 GPU for **30 epochs** using a dataset of ~2,500 public dry recycling images. 

To preserve compilation integrity and prevent training loop crashes on unrepresented categories while our custom campus dataset was being gathered, we engineered **Synthetic Micro-Canvas Placeholders** (microscopic coordinate maps) to safely anchor Class 4 (Organic) and Class 5 (E-Waste).

### Core Validation Metrics (30-Epoch T4 GPU Checkpoint)

| Waste Category | Precision (P) | Recall (R) | mAP50 (Accuracy Index) | Current Status |
| :--- | :---: | :---: | :---: | :--- |
| **Plastic (PET/HDPE)** | **96.2%** | 87.9% | **97.5%** |  Production-Grade |
| **Paper & Cardboard** | **97.2%** | 98.9% | **99.4%** |  Near Perfect |
| **Metal (Alum./Steel)** | **92.8%** | 94.3% | **98.7%** |  Production-Grade |
| **Glass Bottles/Jars** | **91.8%** | 96.9% | **98.1%** |  Production-Grade |
| *Organic Food Waste* | *0.0%* | *0.0%* | *0.0%* |  Bootstrap Placeholder |
| *E-Waste / Hazardous* | *0.0%* | *0.0%* | *0.0%* |  Bootstrap Placeholder |

>  **Technical Inference Note:** The baseline dry recycling modules have already achieved an elite performance profile between **97.5% and 99.4% accuracy**. The mathematical total average (`mAP50: 65.6%`) is temporarily pulled lower purely because Classes 4 and 5 are resting on synthetic placeholder anchors that intentionally register 0% until replaced by real images.

### Pipeline Resilience & Verification Passes

* **Persistent Cloud Bridge:** The entire pipeline mounts directly to cloud folders (`/content/drive/MyDrive/VISION_BIN_PROJECT/runs`), ensuring model weight checkpoints (`last.pt` and `best.pt`) are continuously backed up and immune to runtime disconnects.
* **Late-Stage Recovery Loop:** Solved Google Drive I/O network throttling at epoch 27 by writing an interrupt-resilient automation script (`resume=True`) to finish compiling the production baseline.
* **The Human Isolation Pass:** Subjected the re-wired custom model to out-of-distribution human images. The model yielded **exactly 0 false positive waste detections**. This confirms the system will remain silent and conserve battery power at the edge until a genuine piece of waste is introduced.

---

## 5. Active Roadmap & Next Steps

We are currently entering **Phase 3 & 4 (Local Edge Adaptation)**:

1. **Local Campus Data Ingestion:** Collect 20-30 high-resolution smartphone images per class directly from the IIT Indore campus environment (hostels, labs, cafeterias) under diverse lighting states.
2. **Context Adaptation for Local Indian Brands:** Retrain the model network on localized textures (e.g., Frooti Tetra Paks, crumpled Bisleri bottles, Amul packaging wrappers, and traditional clay *kulhads*).
3. **Weight Fusion & Hardware Deployment:** Replace the structural synthetic placeholders with real annotated data matrices to push the total system average past **95%+ across all 6 categories**, preparing the model size for optimization and final deployment onto microcontroller hardware.
