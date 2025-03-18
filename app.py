import builtins
import os
import sys

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

builtins.sys = sys

from utils.detection_utils import detect_dumpsite, run_detection
from utils.file_utils import cleanup_temp_files, load_coordinates
from utils.model_utils import fix_torch_classes_path, load_model
from utils.translations import translations
from utils.ui_utils import (
    display_detection_results,
    display_sample_images,
    display_waste_samples,
    update_coordinates,
)

load_dotenv()
fix_torch_classes_path()
cleanup_temp_files()

st.set_page_config(page_title="SatelliteGuard", page_icon=":satellite:", layout="wide")

model = load_model()
coords_dict = load_coordinates()

if "language" not in st.session_state:
    st.session_state.language = "en"
if "detection_results" not in st.session_state:
    st.session_state.detection_results = None

selected_language = st.sidebar.radio(
    "Select language / Odaberite jezik",
    options=["English", "Hrvatski"],
    index=0 if st.session_state.language == "en" else 1,
    horizontal=True,
)
st.session_state.language = "en" if selected_language == "English" else "hr"

lang = translations[st.session_state.language]

st.title(lang["title"])
st.write(lang["subtitle"])

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

tab1, tab2 = st.tabs([lang["buildings_land_detection"], lang["waste_detection"]])

with tab1:
    st.header(lang["buildings_land_detection"])

    col1, col2 = st.columns(2)

    with col1:
        # Store previous uploaded file name to detect changes
        if "last_uploaded_file" not in st.session_state:
            st.session_state.last_uploaded_file = None

        # Reset coordinates when changing page states by storing a reset flag
        if "reset_coordinates" not in st.session_state:
            st.session_state.reset_coordinates = False

        def on_file_upload():
            if (
                st.session_state.uploaded_file is not None
                and st.session_state.last_uploaded_file
                != st.session_state.uploaded_file.name
            ):
                st.session_state.last_uploaded_file = (
                    st.session_state.uploaded_file.name
                )
                st.session_state.top_left_x = 0.0
                st.session_state.top_left_y = 0.0
                st.session_state.bottom_right_x = 0.0
                st.session_state.bottom_right_y = 0.0
                st.session_state.reset_coordinates = True
                st.session_state.selected_sample = None
                if "selected_waste_sample" in st.session_state:
                    st.session_state.selected_waste_sample = None

        uploaded_file = st.file_uploader(
            lang["choose_file"],
            type=["jpg", "jpeg", "png"],
            key="uploaded_file",
            on_change=on_file_upload,
        )
        confidence = st.slider(
            lang["confidence"], min_value=0.1, max_value=1.0, value=0.2, step=0.05
        )

    with col2:
        st.subheader(lang["map_coords"])

        # Show warning if coordinates were just reset
        if st.session_state.get("reset_coordinates", False):
            st.warning(lang["coordinates_warning"])
            # Reset the flag after showing warning
            st.session_state.reset_coordinates = False

        tl_col1, tl_col2 = st.columns(2)
        with tl_col1:
            top_left_x = st.number_input(
                lang["top_left_x"],
                value=st.session_state.top_left_x,
                key="input_top_left_x",
            )
            st.session_state.top_left_x = top_left_x
        with tl_col2:
            top_left_y = st.number_input(
                lang["top_left_y"],
                value=st.session_state.top_left_y,
                key="input_top_left_y",
            )
            st.session_state.top_left_y = top_left_y
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

    with st.expander(lang["sample_images"]):
        allowed_samples = ["slika_4.png", "slika_5.png", "slika_6.png"]
        display_sample_images(allowed_samples, coords_dict, lang)

    if st.session_state.selected_sample and uploaded_file is None:
        selected_image = st.session_state.selected_sample
        st.success(f"{lang['selected_sample']} {selected_image}")
        image_path = os.path.join("sample_images", selected_image)
        if os.path.exists(image_path):
            image = Image.open(image_path)
            if update_coordinates(selected_image, coords_dict):
                st.info(lang["coords_loaded"])
            st.subheader(lang["selected_image"])
            st.image(image, use_container_width=True)
            if st.button(lang["run_sample"]):
                cleanup_temp_files()
                with st.spinner(lang["running"]):
                    result_image, detections = run_detection(
                        model,
                        image,
                        [top_left_x, top_left_y],
                        [bottom_right_x, bottom_right_y],
                        confidence,
                        lang,
                    )
                    st.session_state.detection_results = {
                        "image_id": st.session_state.selected_sample,
                        "result_image": result_image,
                        "detections": detections,
                    }

    if uploaded_file is not None:
        st.session_state.selected_sample = None
        if "selected_waste_sample" in st.session_state:
            st.session_state.selected_waste_sample = None

        image = Image.open(uploaded_file)
        if image.mode != "RGB":
            image = image.convert("RGB")
        st.subheader(lang["original_image"])
        st.image(image, use_container_width=True)
        if st.button(lang["run_detection"]):
            cleanup_temp_files()
            with st.spinner(lang["running"]):
                result_image, detections = run_detection(
                    model,
                    image,
                    [top_left_x, top_left_y],
                    [bottom_right_x, bottom_right_y],
                    confidence,
                    lang,
                )
                st.session_state.detection_results = {
                    "image_id": uploaded_file.name,
                    "result_image": result_image,
                    "detections": detections,
                }

    # Determine current image_id
    if uploaded_file is not None:
        current_image_id = uploaded_file.name
    elif st.session_state.selected_sample:
        current_image_id = st.session_state.selected_sample
    else:
        current_image_id = None

    # Display detection results if they exist and match the current image
    if (
        st.session_state.detection_results
        and current_image_id is not None
        and st.session_state.detection_results["image_id"] == current_image_id
    ):
        display_detection_results(
            st.session_state.detection_results["result_image"],
            st.session_state.detection_results["detections"],
            lang,
        )
with tab2:
    st.header(lang["waste_detection"])

    # Initialize session state variables
    if "waste_detection_result" not in st.session_state:
        st.session_state.waste_detection_result = None
    if "current_waste_image" not in st.session_state:
        st.session_state.current_waste_image = None

    with st.expander(lang["waste_samples"]):
        waste_samples = ["barbariga.jpg", "vodnjan_kamenolom.jpg"]
        display_waste_samples(waste_samples, lang)

    # File uploader for custom waste image
    st.subheader(lang["upload_waste_image"])
    waste_uploaded_file = st.file_uploader(
        lang["choose_waste_file"],
        type=["jpg", "jpeg", "png"],
        key="waste_file_uploader",
    )

    if waste_uploaded_file is not None:
        # Check if the image has changed
        image_id = waste_uploaded_file.name
        if st.session_state.current_waste_image != image_id:
            st.session_state.current_waste_image = image_id
            if "waste_detection_result" in st.session_state:
                del st.session_state.waste_detection_result
            if "selected_waste_sample" in st.session_state:
                st.session_state.selected_waste_sample = None

        waste_image = Image.open(waste_uploaded_file)
        if waste_image.mode != "RGB":
            waste_image = waste_image.convert("RGB")
        st.subheader(lang["uploaded_waste_image"])
        st.image(waste_image, use_container_width=True)

        # Detection button with a fixed key
        if st.button(lang["detect_waste"], key="detect_waste_uploaded"):
            with st.spinner(lang["running_waste_detection"]):
                try:
                    is_waste_detected = detect_dumpsite(waste_image)
                    st.session_state.waste_detection_result = is_waste_detected
                except Exception as e:
                    st.session_state.waste_detection_result = f"Error: {str(e)}"

    # Handle selected waste sample
    elif (
        "selected_waste_sample" in st.session_state
        and st.session_state.selected_waste_sample
    ):
        selected_waste_image = st.session_state.selected_waste_sample
        image_id = selected_waste_image
        if st.session_state.current_waste_image != image_id:
            st.session_state.current_waste_image = image_id
            if "waste_detection_result" in st.session_state:
                del st.session_state.waste_detection_result

        # Load and display the sample image
        image_path = os.path.join("sample_images", selected_waste_image)
        if os.path.exists(image_path):
            waste_image = Image.open(image_path)
            st.subheader(lang["selected_image"])
            st.image(waste_image, use_container_width=True)
            button_key = f"detect_waste_btn_{selected_waste_image}"
            if st.button(lang["detect_waste"], key=button_key):
                with st.spinner(lang["running_waste_detection"]):
                    try:
                        is_waste_detected = detect_dumpsite(waste_image)
                        st.session_state.waste_detection_result = is_waste_detected
                    except Exception as e:
                        st.session_state.waste_detection_result = f"Error: {str(e)}"

        # Display the detection result if it exists
        if (
            "waste_detection_result" in st.session_state
            and st.session_state.waste_detection_result is not None
        ):
            if isinstance(st.session_state.waste_detection_result, bool):
                if st.session_state.waste_detection_result:
                    st.error(lang["waste_found"])
                else:
                    st.success(lang["waste_not_found"])
            else:
                st.error(st.session_state.waste_detection_result)

st.sidebar.title(lang["about"])
st.sidebar.info(lang["about_text"])
st.sidebar.title(lang["model_info"])
st.sidebar.info(lang["model_text"])
