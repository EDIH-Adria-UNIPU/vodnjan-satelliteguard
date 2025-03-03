"""
UI utility functions for the SatelliteGuard application.
"""
import os
import streamlit as st
from PIL import Image
import io
import json


def update_coordinates(image_name, coords_dict):
    """
    Update coordinates from the selected sample.
    
    Args:
        image_name: Name of the selected image
        coords_dict: Dictionary of coordinates
        
    Returns:
        bool: True if coordinates were updated, False otherwise
    """
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


def display_sample_images(allowed_samples, coords_dict, lang):
    """
    Display sample images section with clickable images.
    
    Args:
        allowed_samples: List of allowed sample image filenames
        coords_dict: Dictionary of coordinates
        lang: Dictionary of language strings
    """
    st.write(lang["sample_click"])

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
                        # Clear any waste detection selections
                        if "selected_waste_sample" in st.session_state:
                            st.session_state.selected_waste_sample = None
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


def display_waste_samples(waste_samples, lang):
    """
    Display waste disposal sample images.
    
    Args:
        waste_samples: List of waste sample image filenames
        lang: Dictionary of language strings
    """
    st.write(lang["select_waste_sample"])
    
    # Check if sample_images directory exists
    if os.path.exists("sample_images"):
        sample_files = os.listdir("sample_images")
        waste_image_samples = [f for f in sample_files if f in waste_samples]
        
        if waste_image_samples:
            waste_cols = st.columns(min(2, len(waste_image_samples)))
            
            for i, img_name in enumerate(waste_image_samples):
                with waste_cols[i]:
                    img_path = os.path.join("sample_images", img_name)
                    
                    # Create a callback function for each image
                    def select_waste_image_callback(img_name=img_name):
                        st.session_state.selected_waste_sample = img_name
                        # Clear the main sample selection
                        st.session_state.selected_sample = None
                    
                    # Make image clickable
                    if st.button(
                        f"{lang['select']} {img_name}",
                        key=f"waste_btn_{img_name}",
                        on_click=select_waste_image_callback,
                    ):
                        pass  # The actual action happens in the callback
                    
                    # Display the image
                    st.image(Image.open(img_path), caption=img_name, width=200)
        else:
            st.write(lang["no_samples"])
    else:
        st.write(lang["dir_not_found"])


def display_detection_results(result_image, detections, lang):
    """
    Display detection results including image, table, and download options.
    
    Args:
        result_image: Annotated image with detections
        detections: List of detection data
        lang: Dictionary of language strings
    """
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
            # Get status with default value if not present
            status = d.get("status", "")
            
            table_data.append(
                {
                    lang["type"]: d["type"],
                    lang["index"]: d["index"],
                    lang["map_x"]: f"{d['coordinates']['map'][0]:.2f}",
                    lang["map_y"]: f"{d['coordinates']['map'][1]:.2f}",
                    lang["confidence_col"]: f"{d['confidence']:.2f}",
                    lang.get("status", "Status"): status,  # Add status column
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