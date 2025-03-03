import os

import streamlit as st
from PIL import Image
from dotenv import load_dotenv

from utils.file_utils import cleanup_temp_files, load_coordinates
from utils.detection_utils import detect_dumpsite, run_detection
from utils.translations import translations
from utils.ui_utils import update_coordinates, display_sample_images, display_waste_samples, display_detection_results
from utils.model_utils import fix_torch_classes_path, load_model

import sys
import builtins
builtins.sys = sys

load_dotenv()

fix_torch_classes_path()

cleanup_temp_files()

st.set_page_config(page_title="SatelliteGuard", page_icon=":satellite:", layout="wide")

model = load_model()

coords_dict = load_coordinates()

if "language" not in st.session_state:
    st.session_state.language = "en"

selected_language = st.sidebar.radio(
    "Select language / Odaberite jezik",
    options=["English", "Hrvatski"],
    index=0 if st.session_state.language == "en" else 1,
    horizontal=True
)
st.session_state.language = "en" if selected_language == "English" else "hr"

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
        lang["confidence"], min_value=0.1, max_value=1.0, value=0.3, step=0.05
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

# Display sample images section with clickable images
with st.expander(lang["sample_images"]):
    # Define allowed sample images
    allowed_samples = ["slika_1.png", "slika_2.png", "slika_3.png"]
    waste_samples = ["barbariga.jpg", "vodnjan_kamenolom.jpg"]
    
    display_sample_images(allowed_samples, coords_dict, lang)

# Add waste disposal detection section
st.header(lang["waste_detection"])

# Create a section for waste disposal sample images
with st.expander(lang["waste_samples"]):
    display_waste_samples(waste_samples, lang)

# Add a section for uploading custom waste detection images
st.subheader(lang["upload_waste_image"])
waste_uploaded_file = st.file_uploader(
    lang["choose_waste_file"], type=["jpg", "jpeg", "png"], key="waste_file_uploader"
)

# Handle uploaded waste image
if waste_uploaded_file is not None:
    # Clear the selected waste sample when a file is uploaded
    if "selected_waste_sample" in st.session_state:
        st.session_state.selected_waste_sample = None
        
    # Read the image
    waste_image = Image.open(waste_uploaded_file)
    
    # Convert to RGB if needed
    if waste_image.mode != "RGB":
        waste_image = waste_image.convert("RGB")
    
    # Display uploaded image
    st.subheader(lang["uploaded_waste_image"])
    st.image(waste_image, use_container_width=True)
    
    # Run waste detection when user clicks the button
    button_key = f"detect_waste_uploaded_custom_{id(waste_uploaded_file)}"
    if st.button(lang["detect_waste"], key=button_key):
        # Clean up any temporary files before running detection
        cleanup_temp_files()
        
        with st.spinner(lang["running_waste_detection"]):
            # Run waste detection on uploaded image
            is_waste_detected = detect_dumpsite(waste_image)
            
            # Display the result
            if is_waste_detected:
                st.error(lang['waste_found'])
            else:
                st.success(lang['waste_not_found'])

# Handle selected waste sample image for detection
if "selected_waste_sample" in st.session_state and st.session_state.selected_waste_sample:
    selected_waste_image = st.session_state.selected_waste_sample
    st.success(f"{lang['selected_sample']} {selected_waste_image}")
    
    # Load the image
    image_path = os.path.join("sample_images", selected_waste_image)
    if os.path.exists(image_path):
        waste_image = Image.open(image_path)
        
        # Display the selected image
        st.subheader(lang["selected_image"])
        st.image(waste_image, use_container_width=True)
        
        # Run waste detection when user clicks the button
        button_key = f"detect_waste_btn_{selected_waste_image}"
        if st.button(lang["detect_waste"], key=button_key):
            # Clean up any temporary files before running detection
            cleanup_temp_files()
            
            with st.spinner(lang["running_waste_detection"]):
                # Run waste detection
                is_waste_detected = detect_dumpsite(waste_image)
                
                # Display the result
                if is_waste_detected:
                    st.error(lang['waste_found'])
                else:
                    st.success(lang['waste_not_found'])

# Handle selected sample image
if st.session_state.selected_sample:
    selected_image = st.session_state.selected_sample
    st.success(f"{lang['selected_sample']} {selected_image}")

    # Load the image
    image_path = os.path.join("sample_images", selected_image)
    if os.path.exists(image_path):
        image = Image.open(image_path)

        # Update coordinates if available
        if update_coordinates(selected_image, coords_dict):
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
            # Clean up any temporary files before running detection
            cleanup_temp_files()
            
            with st.spinner(lang["running"]):
                # Run detection
                result_image, detections = run_detection(
                    model,
                    image,
                    [top_left_x, top_left_y],
                    [bottom_right_x, bottom_right_y],
                    confidence,
                    lang
                )

                # Display the results
                display_detection_results(result_image, detections, lang)

# Process the uploaded image when available
if uploaded_file is not None:
    # Clear the selected sample when a file is uploaded
    st.session_state.selected_sample = None
    
    # Also clear any waste detection selections
    if "selected_waste_sample" in st.session_state:
        st.session_state.selected_waste_sample = None

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
        # Clean up any temporary files before running detection
        cleanup_temp_files()
        
        with st.spinner(lang["running"]):
            # Run detection
            result_image, detections = run_detection(
                model,
                image,
                [top_left_x, top_left_y],
                [bottom_right_x, bottom_right_y],
                confidence,
                lang
            )

            # Display the results
            display_detection_results(result_image, detections, lang)

st.sidebar.title(lang["about"])
st.sidebar.info(lang["about_text"])

st.sidebar.title(lang["model_info"])
st.sidebar.info(lang["model_text"])
