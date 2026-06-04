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
