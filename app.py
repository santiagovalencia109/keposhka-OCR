import streamlit as st
import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import os
import shutil # Needed to detect Tesseract in the Cloud (Linux)

# ---------------- SMART CONFIGURATION ----------------
# Exact name of your trained data file (without .traineddata extension)
LANGUAGE_NAME = "mcr" 

# Auto-detect Environment: Windows (Local) vs Linux (Cloud)
if os.name == 'nt': # Windows
    # standard path for Windows installation
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else: # Linux (Streamlit Cloud)
    # detecting path automatically in the cloud
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

# ---------------- PATH SETUP ----------------
# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Define tessdata path
tessdata_path = os.path.join(current_dir, 'tessdata')

# Set environment variable so Tesseract finds the language file
os.environ['TESSDATA_PREFIX'] = tessdata_path

# ---------------- UI CONFIGURATION ----------------
st.set_page_config(page_title="My Translator Pro", page_icon="👁️", layout="centered")
st.title("👁️ Keposhka Decoder")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("🔧 Image Settings")
use_filters = st.sidebar.checkbox("Enable image enhancement", value=True)
threshold = st.sidebar.slider(
    "Contrast Threshold (B/W)", 
    0, 255, 128, 
    help="Adjust this until the text looks black and solid, and the background is white."
)

st.sidebar.header("🧠 Reading Mode")
reading_mode = st.sidebar.selectbox(
    "What are you reading?",
    options=["Block of text (Auto)", "Single line", "Single word/character"],
    index=0
)

# Map selection to Tesseract PSM configuration
psm_config = ""
if reading_mode == "Single line":
    psm_config = "--psm 7"
elif reading_mode == "Single word/character":
    psm_config = "--psm 10"
else:
    psm_config = "--psm 3" # Default

# --- MAIN APP ---
uploaded_file = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    original_image = Image.open(uploaded_file)
    image_to_read = original_image # Default to original

    # --- PREVIEW AREA ---
    if use_filters:
        # 1. Convert to Grayscale
        processed_image = original_image.convert('L')
        # 2. Apply Threshold (Binarization)
        processed_image = processed_image.point(lambda p: p > threshold and 255)
        image_to_read = processed_image
        
        st.write("### Comparison:")
        # Create columns: narrow for original, wide for processed
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.caption("Original Thumbnail")
            st.image(original_image, use_container_width=True)
            
        with col2:
            st.caption("What AI sees (Adjust slider)")
            st.image(processed_image, use_container_width=True)
            
    else:
        # If no filters, just show original
        st.image(original_image, caption='Original Image', use_container_width=True)

    # --- TRANSLATION ACTION ---
    st.divider() 
    
    if st.button('Translate now', type="primary", use_container_width=True):
        with st.spinner("Analyzing symbols..."):
            try:
                # We only pass the PSM config here. 
                # Language path is handled by os.environ at the top.
                text = pytesseract.image_to_string(
                    image_to_read, 
                    lang=LANGUAGE_NAME, 
                    config=psm_config
                )
                
                if text.strip():
                    st.success("Read successful!")
                    st.markdown("### Result:")
                    st.text_area("Extracted text:", value=text, height=150)
                else:
                    st.error("No text detected.")
                    st.warning("Tip: Try adjusting the slider or changing the 'Reading Mode' to 'Single line'.")
            
            except Exception as e:
                st.error("Technical error:")
                st.code(e)