"""
Model utility functions for the SatelliteGuard application.
"""
import os
import streamlit as st
from ultralytics import YOLO
import torch


def fix_torch_classes_path():
    """
    Fix for torch.classes.__path__ issue.
    """
    torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)]


@st.cache_resource
def load_model():
    """
    Load the YOLO model with caching.
    
    Returns:
        YOLO: Loaded YOLO model
    """
    return YOLO(os.path.join("models", "satelliteguard-v11.pt")) 