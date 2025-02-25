import io
import json
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import torch
import torchvision
from PIL import Image
from ultralytics import YOLO

# torch.classes.__path__ = []
torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 

# Set page configuration
st.set_page_config(page_title="SatelliteGuard", page_icon="🛰️", layout="wide")

# Translations dictionary
translations = {
    "en": {
        "title": "🛰️ SatelliteGuard",
        "subtitle": "Upload a satellite image and enter coordinates to detect houses and land.",
        "choose_file": "Choose an image file",
        "confidence": "Confidence threshold",
        "map_coords": "Map Coordinates (HTRS96/TM)",
        "top_left_x": "Top-Left X",
        "top_left_y": "Top-Left Y",
        "bottom_right_x": "Bottom-Right X",
        "bottom_right_y": "Bottom-Right Y",
        "sample_images": "Sample Images",
        "sample_click": "Click on a sample image to select it and automatically load its coordinates:",
        "select": "Select",
        "coords_available": "✅ Coordinates available",
        "no_samples": "No allowed sample images found in the sample_images directory.",
        "dir_not_found": "Sample images directory not found.",
        "selected_sample": "Selected sample:",
        "coords_loaded": "Coordinates loaded",
        "selected_image": "Selected Sample Image",
        "run_sample": "Run Detection on Sample",
        "run_detection": "Run Detection",
        "running": "Running detection...",
        "results": "Detection Results",
        "legend": "**Legend:**\n- 🔴 House\n- 🔵 Land",
        "detection_data": "Detection Data",
        "table_view": "Table View",
        "json_view": "JSON View",
        "type": "Type",
        "index": "Index",
        "map_x": "Map X",
        "map_y": "Map Y",
        "confidence_col": "Confidence",
        "download_json": "Download Detection Data (JSON)",
        "download_image": "Download Annotated Image",
        "original_image": "Original Image",
        "about": "About",
        "about_text": """
    **SatelliteGuard Detection**
    
    This application uses a YOLO model to detect houses and land in satellite imagery.
    
    Upload an image, enter the geographic coordinates, and run the detection to visualize 
    and analyze the results.
    """,
        "model_info": "Model Information",
        "model_text": """
    Model: satelliteguard-v9.pt
    
    This model is trained to detect:
    - Houses
    - Land
    """,
        "house": "House",
        "land": "Land",
    },
    "hr": {
        "title": "🛰️ SatelliteGuard",
        "subtitle": "Učitajte satelitsku sliku i unesite koordinate za detekciju kuća i zemljišta.",
        "choose_file": "Odaberite slikovnu datoteku",
        "confidence": "Prag pouzdanosti",
        "map_coords": "Koordinate karte (HTRS96/TM)",
        "top_left_x": "Gornji-lijevi X",
        "top_left_y": "Gornji-lijevi Y",
        "bottom_right_x": "Donji-desni X",
        "bottom_right_y": "Donji-desni Y",
        "sample_images": "Primjeri slika",
        "sample_click": "Kliknite na primjer slike za odabir i automatsko učitavanje koordinata:",
        "select": "Odaberi",
        "coords_available": "✅ Koordinate dostupne",
        "no_samples": "Nema dopuštenih primjera slika u direktoriju sample_images.",
        "dir_not_found": "Direktorij s primjerima slika nije pronađen.",
        "selected_sample": "Odabrani primjer:",
        "coords_loaded": "Koordinate učitane",
        "selected_image": "Odabrana slika",
        "run_sample": "Pokreni detekciju na primjeru",
        "run_detection": "Pokreni detekciju",
        "running": "Detekcija u tijeku...",
        "results": "Rezultati detekcije",
        "legend": "**Legenda:**\n- 🔴 Kuća\n- 🔵 Zemljište",
        "detection_data": "Podaci detekcije",
        "table_view": "Tablični prikaz",
        "json_view": "JSON prikaz",
        "type": "Tip",
        "index": "Indeks",
        "map_x": "Karta X",
        "map_y": "Karta Y",
        "confidence_col": "Pouzdanost",
        "download_json": "Preuzmi podatke detekcije (JSON)",
        "download_image": "Preuzmi označenu sliku",
        "original_image": "Originalna slika",
        "about": "O aplikaciji",
        "about_text": """
    **SatelliteGuard detekcija**
    
    Ova aplikacija koristi YOLO model za detekciju kuća i zemljišta na satelitskim snimkama.
    
    Učitajte sliku, unesite geografske koordinate i pokrenite detekciju za vizualizaciju 
    i analizu rezultata.
    """,
        "model_info": "Informacije o modelu",
        "model_text": """
    Model: satelliteguard-v9.pt
    
    Ovaj model je treniran za detekciju:
    - Kuća
    - Zemljišta
    """,
        "house": "Kuća",
        "land": "Zemljište",
    }
}

# Load the YOLO model
@st.cache_resource
def load_model():
    return YOLO(os.path.join("models", "satelliteguard-v9.pt"))


model = load_model()


# Load coordinates from JSON file if it exists
def load_coordinates():
    if os.path.exists("coordinates.json"):
        with open("coordinates.json", "r") as f:
            return json.load(f)
    return {}


coords_dict = load_coordinates()

# Language selection in sidebar
if "language" not in st.session_state:
    st.session_state.language = "en"

selected_language = st.sidebar.radio(
    "Select language / Odaberite jezik",
    options=["English", "Hrvatski"],
    index=0 if st.session_state.language == "en" else 1,
    horizontal=True
)
st.session_state.language = "en" if selected_language == "English" else "hr"

# Get current language dictionary
lang = translations[st.session_state.language]

st.title(lang["title"])
st.write(lang["subtitle"])

# Session state to track the selected sample image
if "selected_sample" not in st.session_state:
    st.session_state.selected_sample = None
if "top_left_x" not in st.session_state:
    st.session_state.top_left_x = 291083.58
if "top_left_y" not in st.session_state:
    st.session_state.top_left_y = 4984222.26
if "bottom_right_x" not in st.session_state:
    st.session_state.bottom_right_x = 291564.66
if "bottom_right_y" not in st.session_state:
    st.session_state.bottom_right_y = 4983991.71

# Create two columns for the form
col1, col2 = st.columns(2)

with col1:
    # File uploader
    uploaded_file = st.file_uploader(
        lang["choose_file"], type=["jpg", "jpeg", "png"]
    )

    # Confidence threshold
    confidence = st.slider(
        lang["confidence"], min_value=0.1, max_value=1.0, value=0.4, step=0.05
    )

with col2:
    # Coordinate inputs
    st.subheader(lang["map_coords"])

    # Create two columns for top-left coordinates
    tl_col1, tl_col2 = st.columns(2)
    with tl_col1:
        top_left_x = st.number_input(
            lang["top_left_x"], value=st.session_state.top_left_x, key="input_top_left_x"
        )
        st.session_state.top_left_x = top_left_x
    with tl_col2:
        top_left_y = st.number_input(
            lang["top_left_y"], value=st.session_state.top_left_y, key="input_top_left_y"
        )
        st.session_state.top_left_y = top_left_y

    # Create two columns for bottom-right coordinates
    br_col1, br_col2 = st.columns(2)
    with br_col1:
        bottom_right_x = st.number_input(
            lang["bottom_right_x"],
            value=st.session_state.bottom_right_x,
            key="input_bottom_right_x",
        )
        st.session_state.bottom_right_x = bottom_right_x
    with br_col2:
        bottom_right_y = st.number_input(
            lang["bottom_right_y"],
            value=st.session_state.bottom_right_y,
            key="input_bottom_right_y",
        )
        st.session_state.bottom_right_y = bottom_right_y


# Function to run detection
def run_detection(image, top_left, bottom_right, confidence_threshold):
    Tx, Ty = top_left
    Bx, By = bottom_right

    # Convert to a NumPy array for processing
    img_array = np.array(image)
    img_height, img_width = img_array.shape[:2]

    # Convert to a NumPy BGR image for OpenCV drawing
    predicted_image_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    temp_img_path = os.path.join("temp_image.png")
    rgb_image = image.convert("RGB")
    rgb_image.save(temp_img_path)

    # Run YOLO model on the image file path instead of the array
    results = model(temp_img_path, conf=confidence_threshold)

    # Clean up the temporary file
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)

    house_index = 0
    land_index = 0

    # Create a list to store detection data
    detections = []

    for result in results:
        boxes = result.boxes.data
        for box in boxes:
            x1, y1, x2, y2, confidence, class_id = box.tolist()
            class_id = int(class_id)

            # Calculate center of the bounding box
            center_x_pix = (x1 + x2) / 2.0
            center_y_pix = (y1 + y2) / 2.0

            # Convert pixel coordinates to map coordinates (HTRS96/TM)
            center_x_map = Tx + (center_x_pix / img_width) * (Bx - Tx)
            center_y_map = Ty + (center_y_pix / img_height) * (By - Ty)

            if class_id == 0:
                color = (0, 0, 255)  # Red for houses (BGR format)
                label = str(house_index)
                house_index += 1
                object_type = lang["house"]
            else:
                color = (255, 0, 0)  # Blue for land (BGR format)
                label = str(land_index)
                land_index += 1
                object_type = lang["land"]

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

            # Add detection to the list
            detections.append(
                {
                    "type": object_type,
                    "index": label,
                    "coordinates": {
                        "pixel": [float(center_x_pix), float(center_y_pix)],
                        "map": [float(center_x_map), float(center_y_map)],
                    },
                    "confidence": float(confidence),
                }
            )

    # Convert back to RGB for display
    predicted_image_rgb = cv2.cvtColor(predicted_image_bgr, cv2.COLOR_BGR2RGB)

    return predicted_image_rgb, detections


# Function to update coordinates from the selected sample
def update_coordinates(image_name):
    if image_name in coords_dict:
        coords = coords_dict[image_name]
        if "top-left" in coords and "bottom-right" in coords:
            # Update session state with new coordinates
            st.session_state.top_left_x = coords["top-left"][0]
            st.session_state.top_left_y = coords["top-left"][1]
            st.session_state.bottom_right_x = coords["bottom-right"][0]
            st.session_state.bottom_right_y = coords["bottom-right"][1]
            return True
    return False


# Display sample images section with clickable images
with st.expander(lang["sample_images"]):
    st.write(lang["sample_click"])

    # Define allowed sample images
    allowed_samples = ["slika_1.png", "slika_2.png", "slika_3.png"]

    # Check if sample_images directory exists
    if os.path.exists("sample_images"):
        sample_files = os.listdir("sample_images")
        sample_images = [f for f in sample_files if f in allowed_samples]

        if sample_images:
            sample_cols = st.columns(min(3, len(sample_images)))

            for i, img_name in enumerate(sample_images):
                with sample_cols[i]:
                    img_path = os.path.join("sample_images", img_name)

                    # Create a callback function for each image
                    def select_image_callback(img_name=img_name):
                        st.session_state.selected_sample = img_name
                        # Immediately update coordinates when the image is selected
                        if img_name in coords_dict:
                            coords = coords_dict[img_name]
                            if "top-left" in coords and "bottom-right" in coords:
                                st.session_state.top_left_x = coords["top-left"][0]
                                st.session_state.top_left_y = coords["top-left"][1]
                                st.session_state.bottom_right_x = coords[
                                    "bottom-right"
                                ][0]
                                st.session_state.bottom_right_y = coords[
                                    "bottom-right"
                                ][1]

                    # Make image clickable with immediate coordinate update
                    if st.button(
                        f"{lang['select']} {img_name}",
                        key=f"btn_{img_name}",
                        on_click=select_image_callback,
                    ):
                        pass  # The actual action happens in the callback

                    # Display the image
                    st.image(Image.open(img_path), caption=img_name, width=200)

                    # Show if coordinates are available
                    if img_name in coords_dict:
                        st.write(lang["coords_available"])
        else:
            st.write(lang["no_samples"])
    else:
        st.write(lang["dir_not_found"])

# Handle selected sample image
if st.session_state.selected_sample:

    selected_image = st.session_state.selected_sample
    st.success(f"{lang['selected_sample']} {selected_image}")

    # Load the image
    image_path = os.path.join("sample_images", selected_image)
    if os.path.exists(image_path):
        image = Image.open(image_path)

        # Update coordinates if available
        if update_coordinates(selected_image):
            st.info(lang["coords_loaded"])
            # Use the updated values from session state
            top_left_x = st.session_state.top_left_x
            top_left_y = st.session_state.top_left_y
            bottom_right_x = st.session_state.bottom_right_x
            bottom_right_y = st.session_state.bottom_right_y

        # Display the selected image
        st.subheader(lang["selected_image"])
        st.image(image, use_container_width=True)

        # Run detection when user clicks the button
        if st.button(lang["run_sample"]):
            with st.spinner(lang["running"]):
                # Run detection
                result_image, detections = run_detection(
                    image,
                    [top_left_x, top_left_y],
                    [bottom_right_x, bottom_right_y],
                    confidence,
                )

                # Display the result
                st.subheader(lang["results"])
                st.image(result_image, use_container_width=True)

                # Create a legend
                st.markdown(lang["legend"])

                # Display detection data
                st.subheader(lang["detection_data"])

                # Create tabs for different views of the data
                tab1, tab2 = st.tabs([lang["table_view"], lang["json_view"]])

                with tab1:
                    # Prepare data for the table
                    table_data = []
                    for d in detections:
                        table_data.append(
                            {
                                lang["type"]: d["type"],
                                lang["index"]: d["index"],
                                lang["map_x"]: f"{d['coordinates']['map'][0]:.2f}",
                                lang["map_y"]: f"{d['coordinates']['map'][1]:.2f}",
                                lang["confidence_col"]: f"{d['confidence']:.2f}",
                            }
                        )

                    # Display as a table
                    st.dataframe(table_data)

                with tab2:
                    # Display as JSON
                    st.json(detections)

                # Option to download the detection data
                json_str = json.dumps(detections, indent=2)
                st.download_button(
                    label=lang["download_json"],
                    data=json_str,
                    file_name="detection_data.json",
                    mime="application/json",
                )

                # Option to download the annotated image
                buf = io.BytesIO()
                Image.fromarray(result_image).save(buf, format="PNG")
                st.download_button(
                    label=lang["download_image"],
                    data=buf.getvalue(),
                    file_name="annotated_image.png",
                    mime="image/png",
                )

# Process the uploaded image when available
if uploaded_file is not None:
    # Clear the selected sample when a file is uploaded
    st.session_state.selected_sample = None

    # Read the image
    image = Image.open(uploaded_file)

    # Convert to RGB if needed
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Display original image
    st.subheader(lang["original_image"])
    st.image(image, use_container_width=True)

    # Run detection when user clicks the button
    if st.button(lang["run_detection"]):
        with st.spinner(lang["running"]):
            # Run detection
            result_image, detections = run_detection(
                image,
                [top_left_x, top_left_y],
                [bottom_right_x, bottom_right_y],
                confidence,
            )

            # Display the result
            st.subheader(lang["results"])
            st.image(result_image, use_container_width=True)

            # Create a legend
            st.markdown(lang["legend"])

            # Display detection data
            st.subheader(lang["detection_data"])

            # Create tabs for different views of the data
            tab1, tab2 = st.tabs([lang["table_view"], lang["json_view"]])

            with tab1:
                # Prepare data for the table
                table_data = []
                for d in detections:
                    table_data.append(
                        {
                            lang["type"]: d["type"],
                            lang["index"]: d["index"],
                            lang["map_x"]: f"{d['coordinates']['map'][0]:.2f}",
                            lang["map_y"]: f"{d['coordinates']['map'][1]:.2f}",
                            lang["confidence_col"]: f"{d['confidence']:.2f}",
                        }
                    )

                # Display as a table
                st.dataframe(table_data)

            with tab2:
                # Display as JSON
                st.json(detections)

            # Option to download the detection data
            json_str = json.dumps(detections, indent=2)
            st.download_button(
                label=lang["download_json"],
                data=json_str,
                file_name="detection_data.json",
                mime="application/json",
            )

            # Option to download the annotated image
            buf = io.BytesIO()
            Image.fromarray(result_image).save(buf, format="PNG")
            st.download_button(
                label=lang["download_image"],
                data=buf.getvalue(),
                file_name="annotated_image.png",
                mime="image/png",
            )

st.sidebar.title(lang["about"])
st.sidebar.info(lang["about_text"])

st.sidebar.title(lang["model_info"])
st.sidebar.info(lang["model_text"])
