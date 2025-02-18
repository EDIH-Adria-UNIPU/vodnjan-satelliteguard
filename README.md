# SatelliteGuard

A computer vision system developed for the City of Vodnjan that uses satellite imagery to detect buildings, agricultural land usage, and illegal waste disposal sites.

## Overview

SatelliteGuard combines multiple AI models to analyze satellite images and detect:

- Buildings/structures (YOLO)
- Agricultural land areas (YOLO)
- Waste disposal sites (Gemini 2.0 Flash)

## Technical Implementation

- Building and land detection based on YOLO (You Only Look Once) architecture
- Uses Ultralytics YOLOv11 framework for primary object detection
- Waste disposal detection powered by Google's Gemini 2.0 Flash model
- Processes satellite imagery to identify and classify objects
- Requires georeferenced images for location context

## YOLO Model Versions

- v5 - detects only houses
- v7, v8 - detects houses and land

See `satelliteguard.ipynb` for implementation details and usage examples.
