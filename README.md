# SatelliteGuard

A computer vision system developed for the City of Vodnjan that uses satellite imagery to detect buildings and agricultural land usage.

## Overview

SatelliteGuard is a fine-tuned YOLO model that analyzes satellite images to detect:

- Buildings/structures
- Agricultural land areas

## Technical Implementation

- Based on YOLO (You Only Look Once) architecture
- Uses Ultralytics YOLOv11 framework
- Processes satellite imagery to identify and classify objects
- Requires georeferenced images for location context

## Model Versions

- v5 - detects only houses
- v7, v8 - detects houses and land

## Usage

```python
from ultralytics import YOLO
model = YOLO("models/satelliteguard-v8.pt")
results = model("image.png", conf=0.4)
```

## Project Status

This is a prototype implementation focusing on basic detection capabilities. Geographic coordinates must be provided alongside the input images.
