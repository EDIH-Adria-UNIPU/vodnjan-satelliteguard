"""
Translation strings for the SatelliteGuard application.
"""

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
        "legend": "**Legend:**\n- 🟢 Object data exists\n- 🔴 Object data does not exist\n- 🔵 Detected agricultural area\n- 🟠 Undetected agricultural area",
        "detection_data": "Detection Data",
        "table_view": "Table View",
        "json_view": "JSON View",
        "type": "Type",
        "index": "Index",
        "map_x": "Map X",
        "map_y": "Map Y",
        "confidence_col": "Confidence",
        "status": "Status",
        "legal": "Data exists",
        "illegal": "No data found",
        "detected": "Detected",
        "undetected": "Undetected",
        "document": "Document",
        "cadastral_municipality": "Cadastral Municipality",
        "download_json": "Download Detection Data (JSON)",
        "download_excel": "Download Detection Data (Excel)",
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
    Model: satelliteguard-v11.pt
    
    This model is trained to detect:
    - Houses
    - Land
    """,
        "house": "House",
        "land": "Land",
        "waste_detection": "Illegal Waste Disposal Detection",
        "detect_waste": "Detect Illegal Waste",
        "running_waste_detection": "Running waste detection...",
        "waste_found": "An illegal waste disposal site has been detected in this image!",
        "waste_not_found": "No illegal waste disposal site detected in this image.",
        "waste_samples": "Waste Disposal Sample Images",
        "select_waste_sample": "Select a waste disposal sample image:",
        "upload_waste_image": "Upload Your Own Image for Waste Detection",
        "choose_waste_file": "Choose an image file for waste detection",
        "uploaded_waste_image": "Uploaded Image for Waste Detection",
        "buildings_land_detection": "Buildings & Land Detection",
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
        "legend": "**Legenda:**\n- 🟢 Podaci za objekt postoje\n- 🔴 Podaci za objekt ne postoje\n- 🔵 Detektirano poljoprivredno zemljište\n- 🟠 Nedetektirano poljoprivredno zemljište",
        "detection_data": "Podaci detekcije",
        "table_view": "Tablični prikaz",
        "json_view": "JSON prikaz",
        "type": "Tip",
        "index": "Indeks",
        "map_x": "Karta X",
        "map_y": "Karta Y",
        "confidence_col": "Pouzdanost",
        "status": "Status",
        "legal": "Podaci postoje",
        "illegal": "Nema podataka",
        "detected": "Detektirano",
        "undetected": "Nedetektirano",
        "document": "Dokument",
        "cadastral_municipality": "Katastarska općina",
        "download_json": "Preuzmi podatke detekcije (JSON)",
        "download_excel": "Preuzmi podatke detekcije (Excel)",
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
    Model: satelliteguard-v11.pt
    
    Ovaj model je treniran za detekciju:
    - Kuća
    - Zemljišta
    """,
        "house": "Kuća",
        "land": "Zemljište",
        "waste_detection": "Detekcija ilegalnog odlagališta otpada",
        "detect_waste": "Detektiraj ilegalno odlagalište",
        "running_waste_detection": "Detekcija otpada u tijeku...",
        "waste_found": "Na ovoj slici nalazi se deponij otpada!",
        "waste_not_found": "Na ovoj slici ne nalazi se deponij otpada.",
        "waste_samples": "Primjeri slika odlagališta otpada",
        "select_waste_sample": "Odaberite primjer slike odlagališta otpada:",
        "upload_waste_image": "Učitajte vlastitu sliku za detekciju otpada",
        "choose_waste_file": "Odaberite slikovnu datoteku za detekciju otpada",
        "uploaded_waste_image": "Učitana slika za detekciju otpada",
        "buildings_land_detection": "Detekcija zgrada i zemljišta",
    }
} 