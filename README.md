# SatelliteGuard

A computer vision system developed for the City of Vodnjan that uses satellite imagery to detect buildings, agricultural land usage, and illegal waste disposal sites.

## Overview

SatelliteGuard combines multiple AI models to analyze satellite images and detect:

- Buildings/structures (YOLOv12)
- Agricultural land areas (YOLOv12)
- Waste disposal sites (Gemini 2.0 Flash)

## Technical Implementation

- Building and land detection based on YOLO (You Only Look Once) architecture
- Waste disposal detection powered by Google's Gemini 2.0 Flash model
- Processes satellite imagery to identify and classify objects
- Requires georeferenced images for location context
  - Coordinates provided via coordinates.json in HTRS96/TM format
  - Each image requires top-left and bottom-right corner coordinates

See `satelliteguard.ipynb` for implementation details and usage examples.
