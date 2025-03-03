"""
File utility functions for the SatelliteGuard application.
"""
import os
import json
import uuid


def cleanup_temp_files():
    """
    Clean up any temporary files created during detection.
    """
    for file in os.listdir():
        if file.startswith("temp_image_") or file.startswith("temp_waste_image_"):
            try:
                os.remove(file)
            except:
                pass


def load_coordinates():
    """
    Load coordinates from JSON file if it exists.
    
    Returns:
        dict: Dictionary of coordinates or empty dict if file doesn't exist.
    """
    if os.path.exists("coordinates.json"):
        with open("coordinates.json", "r") as f:
            return json.load(f)
    return {}


def create_temp_image(image, prefix="temp_image_"):
    """
    Create a temporary image file and return its path.
    
    Args:
        image: PIL Image object
        prefix: Prefix for the temporary file name
        
    Returns:
        str: Path to the temporary image file
    """
    temp_id = str(uuid.uuid4())
    temp_img_path = os.path.join(f"{prefix}{temp_id}.jpg")
    rgb_image = image.convert("RGB")
    rgb_image.save(temp_img_path)
    return temp_img_path 