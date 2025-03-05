"""
Detection utility functions for the SatelliteGuard application.
"""
import os
import cv2
import numpy as np
import json
from google import genai
from google.genai import types
from utils.file_utils import create_temp_image


def detect_dumpsite(image):
    """
    Detect illegal waste disposal in an image using Gemini API.
    
    Args:
        image: PIL Image object
        
    Returns:
        bool: True if waste is detected, False otherwise
    """
    try:
        # Create a unique temporary file to save the image
        temp_img_path = create_temp_image(image, prefix="temp_waste_image_")
        
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        PROMPT = "Does this image contain an illegal dumpsite?"

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction="Return a JSON object with the key 'result' and a boolean value true or false.",
                temperature=0.1,
                response_mime_type="application/json"
            ),
            contents=[PROMPT, image])
        
        # Clean up the temporary file
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
            
        print(response.text)

        return json.loads(response.text)["result"]
    except Exception as e:
        print(f"Error detecting waste: {e}")
        # Make sure to clean up even if there's an error
        if 'temp_img_path' in locals() and os.path.exists(temp_img_path):
            os.remove(temp_img_path)
        return False


def run_detection(model, image, top_left, bottom_right, confidence_threshold, lang):
    """
    Run object detection on an image.
    
    Args:
        model: YOLO model
        image: PIL Image object
        top_left: [x, y] coordinates of top-left corner
        bottom_right: [x, y] coordinates of bottom-right corner
        confidence_threshold: Confidence threshold for detection
        lang: Dictionary of language strings
        
    Returns:
        tuple: (predicted_image_rgb, detections)
    """
    # Load legal objects and agricultural areas data
    try:
        with open(os.path.join("data", "legalni_objekti.json"), "r") as f:
            legal_objects = json.load(f)
    except Exception as e:
        print(f"Error loading legal objects: {e}")
        legal_objects = []
        
    try:
        with open(os.path.join("data", "povrsine.json"), "r") as f:
            agricultural_areas = json.load(f)
    except Exception as e:
        print(f"Error loading agricultural areas: {e}")
        agricultural_areas = []
    
    Tx, Ty = top_left
    Bx, By = bottom_right

    # Convert to a NumPy array for processing
    img_array = np.array(image)
    img_height, img_width = img_array.shape[:2]

    # Convert to a NumPy BGR image for OpenCV drawing
    predicted_image_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # Create a unique temporary file
    temp_img_path = create_temp_image(image)

    try:
        # Run YOLO model on the image file path instead of the array
        results = model(temp_img_path, conf=confidence_threshold)

        # Clean up the temporary file
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)

        house_index = 0
        land_index = 0
        detected_agr_areas = []

        # Create a list to store detection data
        detections = []

        for result in results:
            boxes = result.boxes.data
            for box in boxes:
                x1, y1, x2, y2, confidence, class_id = box.tolist()
                class_id = int(class_id)

                # Skip detections with low confidence
                if class_id == 0 and confidence < 0.3:
                    continue
                elif class_id == 1 and confidence < 0.2:
                    continue

                # Calculate center of the bounding box
                center_x_pix = (x1 + x2) / 2.0
                center_y_pix = (y1 + y2) / 2.0

                # Convert pixel coordinates to map coordinates (HTRS96/TM)
                center_x_map = Tx + (center_x_pix / img_width) * (Bx - Tx)
                center_y_map = Ty + (center_y_pix / img_height) * (By - Ty)

                if class_id == 0:  # House
                    label = str(house_index)
                    house_index += 1
                    object_type = lang["house"]
                    
                    # Check against legal objects
                    is_legal = False
                    matching_obj = None
                    for obj in legal_objects:
                        if abs(center_x_map - obj["x_coord"]) < 10 and abs(center_y_map - obj["y_coord"]) < 10:
                            print(f"Detected house {label} matches legal object {obj['broj_kat_cestice']}")
                            is_legal = True
                            matching_obj = obj
                            break
                    
                    if is_legal:
                        color = (0, 255, 0)  # Green for legal houses (BGR format)
                        object_status = lang.get("legal", "legal")
                    else:
                        color = (0, 0, 255)  # Red for illegal houses (BGR format)
                        object_status = lang.get("illegal", "illegal")
                        
                else:  # Agricultural area
                    color = (255, 0, 0)  # Blue for agricultural areas (BGR format)
                    label = str(land_index)
                    land_index += 1
                    object_type = lang["land"]
                    object_status = lang.get("detected", "detected")
                    
                    # Check if this agricultural area is in our database
                    matching_area = None
                    for povrsina in agricultural_areas:
                        if abs(center_x_map - povrsina["x_coord"]) < 15 and abs(center_y_map - povrsina["y_coord"]) < 15:
                            detected_agr_areas.append(povrsina["x_coord"])
                            detected_agr_areas.append(povrsina["y_coord"])
                            matching_area = povrsina
                            break

                # Draw dot
                cv2.circle(
                    predicted_image_bgr,
                    (int(center_x_pix), int(center_y_pix)),
                    radius=5,
                    color=color,
                    thickness=-1,
                )

                # Draw label
                cv2.putText(
                    predicted_image_bgr,
                    label,
                    (int(center_x_pix), int(center_y_pix) - 10),  # slightly above the dot
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,  # font scale
                    color,  # text color
                    2,  # line thickness
                    cv2.LINE_AA,
                )

                # Create detection dictionary
                detection_dict = {
                    "type": object_type,
                    "index": label,
                    "coordinates": {
                        "pixel": [float(center_x_pix), float(center_y_pix)],
                        "map": [float(center_x_map), float(center_y_map)],
                    },
                    "confidence": float(confidence),
                    "status": object_status
                }
                
                # Add document information for legal buildings
                if class_id == 0 and matching_obj:
                    detection_dict["dokument"] = matching_obj["dokument"]
                    detection_dict["broj_kat_cestice"] = matching_obj["broj_kat_cestice"]
                
                # Add cadastral municipality for agricultural areas
                if class_id == 1 and matching_area:
                    detection_dict["dokument"] = matching_area["dokument"]
                    detection_dict["kat_opcina"] = matching_area["kat_opcina"]
                    detection_dict["broj_kat_cestice"] = matching_area["broj_kat_cestice"]
                
                # Add detection to the list
                detections.append(detection_dict)
        
        # Check for agricultural areas that weren't detected
        for area in agricultural_areas:
            x_map = area["x_coord"]
            y_map = area["y_coord"]
            
            # Check if this agricultural area is within the image bounds
            if Tx <= x_map <= Bx and By <= y_map <= Ty:
                if x_map not in detected_agr_areas or y_map not in detected_agr_areas:
                    # Convert map coordinates to pixel coordinates
                    x_pix = ((x_map - Tx) / (Bx - Tx)) * img_width
                    y_pix = ((y_map - Ty) / (By - Ty)) * img_height
                    
                    # Mark undetected agricultural areas with orange
                    cv2.circle(
                        predicted_image_bgr,
                        (int(x_pix), int(y_pix)),
                        radius=5,
                        color=(0, 165, 255),  # Orange in BGR
                        thickness=-1
                    )
                    
                    # Add label for undetected agricultural area
                    cv2.putText(
                        predicted_image_bgr,
                        label,
                        (int(x_pix), int(y_pix) - 10),  # slightly above the dot
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,  # font scale
                        (0, 165, 255),  # Orange in BGR
                        2,  # line thickness
                        cv2.LINE_AA,
                    )
                    
                    # Add to detections list
                    label = str(land_index)
                    land_index += 1
                    
                    detections.append(
                        {
                            "type": lang["land"],
                            "index": label,
                            "coordinates": {
                                "pixel": [float(x_pix), float(y_pix)],
                                "map": [float(x_map), float(y_map)],
                            },
                            "confidence": 1.0,  # Known location
                            "status": lang.get("undetected", "undetected"),
                            "dokument": area["dokument"],
                            "kat_opcina": area["kat_opcina"],
                            "broj_kat_cestice": area["broj_kat_cestice"]
                        }
                    )
                    
                    print(f"Warning: Agricultural area {area['broj_kat_cestice']} not detected by model")

        # Convert back to RGB for display
        predicted_image_rgb = cv2.cvtColor(predicted_image_bgr, cv2.COLOR_BGR2RGB)

        return predicted_image_rgb, detections
    except Exception as e:
        # Make sure to clean up even if there's an error
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
        print(f"Error in detection: {e}")
        return img_array, [] 