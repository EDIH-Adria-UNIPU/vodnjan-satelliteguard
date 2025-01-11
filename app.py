import os

import streamlit as st
from ultralytics import YOLO

st.image(os.path.join("assets", "vodnjan-logo.png"), width=100)

st.title("Satelliteguard")

uploaded_image = st.file_uploader("Učitajte sliku", type=("jpg", "jpeg", "png"))

model = YOLO("satelliteguard-v5.pt")

if uploaded_image is not None:

    # Save the uploaded image
    with open("uploaded_image.jpg", "wb") as f:
        f.write(uploaded_image.getbuffer())

    img = "uploaded_image.jpg"

    results = model(img)

    for result in results:
        boxes = result.boxes
        result.save(filename="result.jpg")

    # Display the result
    st.image("result.jpg")

    # Delete the uploaded image
    os.remove("uploaded_image.jpg")
