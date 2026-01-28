import streamlit as st
import pytesseract
from PIL import Image, ImageOps
import os
import shutil 

# ---------------- CONFIGURATION ----------------
LANGUAGE_NAME = "mcr" 

# Auto-detect Environment
if os.name == 'nt': # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else: # Linux (Cloud)
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

# Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
tessdata_path = os.path.join(current_dir, 'tessdata')
os.environ['TESSDATA_PREFIX'] = tessdata_path

# ---------------- UI CONFIGURATION ----------------
st.set_page_config(page_title="Keposhka Decoder by Santiago109", page_icon="👁️", layout="centered")
st.title("👁️ Keposhka Decoder")

# Keep the Reading Mode in Sidebar as it is a "setup" config
st.sidebar.header("🧠 Reading Mode")
reading_mode = st.sidebar.selectbox(
    "What are you reading?",
    options=["Block of text (Auto)", "Single line", "Single word/character"],
    index=0
)

# Map PSM
psm_config = ""
if reading_mode == "Single line":
    psm_config = "--psm 7"
elif reading_mode == "Single word/character":
    psm_config = "--psm 10"
else:
    psm_config = "--psm 3"

# ---------------- MAIN APP ----------------
uploaded_file = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    original_image = Image.open(uploaded_file)
    
    # 1. IMAGE CONTROLS (Above thumbnails)
    st.subheader("🛠️ Image Adjustments")
    
    # Control Row
    col_ctrl1, col_ctrl2 = st.columns(2)
    
    with col_ctrl1:
        # Checkbox to Invert Colors (Fix for white text on black background)
        invert_image = st.checkbox("Invert colors (for white text)", value=False)
        
    with col_ctrl2:
        # Checkbox to enable/disable filters completely
        use_filters = st.checkbox("Enable high contrast", value=True)

    # Slider is now visible in the main area
    if use_filters:
        threshold = st.slider(
            "Contrast Threshold (Adjust to make text black & solid)", 
            0, 255, 128
        )
    
    # 2. IMAGE PROCESSING
    # Start with original
    image_to_process = original_image.convert('RGB')

    # Step A: Inversion (If text is white)
    if invert_image:
        image_to_process = ImageOps.invert(image_to_process)
    
    # Step B: Contrast/Binarization
    if use_filters:
        # Convert to Grayscale
        processed_image = image_to_process.convert('L')
        # Apply Threshold
        processed_image = processed_image.point(lambda p: p > threshold and 255)
        image_final = processed_image
    else:
        # If filters disabled, just use the (potentially inverted) image
        image_final = image_to_process

    # 3. THUMBNAILS PREVIEW
    st.write("### Preview:")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.caption("Original")
        st.image(original_image, use_container_width=True)
        
    with col2:
        st.caption("What AI sees (Final input)")
        st.image(image_final, use_container_width=True)

    # 4. TRANSLATE ACTION
    st.divider() 
    
    if st.button('Translate now', type="primary", use_container_width=True):
        with st.spinner("Analyzing symbols..."):
            try:
                text = pytesseract.image_to_string(
                    image_final, 
                    lang=LANGUAGE_NAME, 
                    config=psm_config
                )
                
                if text.strip():
                    st.success("Read successful!")
                    st.markdown("### Result:")
                    st.text_area("Extracted text:", value=text, height=150)
                else:
                    st.error("No text detected.")
                    st.warning("Tip: Try checking 'Invert colors' or adjusting the slider.")
            
            except Exception as e:
                st.error("Technical error:")
                st.code(e)