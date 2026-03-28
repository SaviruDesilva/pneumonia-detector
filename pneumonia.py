import streamlit as st
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
import numpy as np
from PIL import Image
import joblib
import cv2

# --- AUTHENTICATION SECTION ---
if not st.user.is_logged_in:
    st.title("🛡️ Secure Access Control")
    st.warning("Please log in to use the Pneumonia Detector.")

    # Pass the name of the config block from your secrets.toml
    if st.button("Log in with Asgardeo"):
        st.login("asgardeo") 
    st.stop()
# Page configuration
st.set_page_config(
    page_title="Pneumonia Detection",
    page_icon="🫁",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    .normal {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .pneumonia {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Load model and threshold
@st.cache_resource
def load_model():
    try:
        model = tf.keras.models.load_model('pneumonia_model.h5')
        return model
    except:
        st.error("⚠️ Model file 'pneumonia_model.h5' not found. Please ensure the model is saved in the same directory.")
        return None

@st.cache_data
def load_metadata():
    try:
        class_names = joblib.load("class_names.pkl")
        decision_threshold = joblib.load("decision_threshold.pkl")
        return class_names, decision_threshold
    except:
        st.warning("⚠️ Metadata files not found. Using default values.")
        return ['NORMAL', 'PNEUMONIA'], 0.65

# Image quality validation function
def validate_image_quality(img):
    """
    Check if the image is clear enough for analysis
    Returns: (is_valid, message, quality_score)
    """
    img_array = np.array(img.convert('L'))  # Convert to grayscale
    
    # Check 1: Image sharpness (using Laplacian variance)
    laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()
    
    # Check 2: Brightness (mean pixel value)
    brightness = np.mean(img_array)
    
    # Check 3: Contrast (standard deviation)
    contrast = np.std(img_array)
    
    # Check 4: Check if image is too dark or too bright
    dark_pixels = np.sum(img_array < 30) / img_array.size
    bright_pixels = np.sum(img_array > 225) / img_array.size
    
    # Quality thresholds
    min_sharpness = 100
    min_contrast = 20
    max_dark_ratio = 0.7
    max_bright_ratio = 0.7
    min_brightness = 20
    max_brightness = 235
    
    issues = []
    
    # Validate sharpness
    if laplacian_var < min_sharpness:
        issues.append("Image is too blurry or out of focus")
    
    # Validate contrast
    if contrast < min_contrast:
        issues.append("Image has very low contrast")
    
    # Validate brightness
    if brightness < min_brightness:
        issues.append("Image is too dark")
    elif brightness > max_brightness:
        issues.append("Image is overexposed")
    
    # Validate dark/bright pixel ratios
    if dark_pixels > max_dark_ratio:
        issues.append("Image has too many dark areas")
    if bright_pixels > max_bright_ratio:
        issues.append("Image has too many bright/washed out areas")
    
    # Calculate overall quality score (0-100)
    quality_score = min(100, (
        (laplacian_var / 500 * 40) +  # Sharpness contributes 40%
        (contrast / 100 * 30) +         # Contrast contributes 30%
        (30 if 50 < brightness < 200 else 15)  # Brightness contributes 30%
    ))
    
    is_valid = len(issues) == 0
    message = " | ".join(issues) if issues else "Image quality is acceptable"
    
    return is_valid, message, quality_score

# Prediction function
def predict_image(model, img, decision_threshold):
    # Preprocess image
    img = img.resize((128, 128))
    img_array = np.array(img)
    
    # Handle grayscale images
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=-1)
    
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    pred = model.predict(img_array, verbose=0)
    pred_value = pred[0][0]
    
    return pred_value

# Main app
def main():
    # Header
    st.markdown('<p class="main-header">🫁 Pneumonia Detection System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload a chest X-ray image to detect bacterial and viral pneumonia</p>', unsafe_allow_html=True)
    
    # Load model and metadata
    model = load_model()
    class_names, decision_threshold = load_metadata()
    
    if model is None:
        st.stop()
    
    # Sidebar information
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("""
        This application uses a deep learning model to detect bacterial and viral pneumonia from chest X-ray images.
        
        **How to use:**
        1. Upload a chest X-ray image
        2. Wait for quality validation
        3. Analyze and view results
        
        **Model Details:**
        - Input size: 128x128 pixels
        - Architecture: CNN with data augmentation
        - Classes: Normal, Pneumonia
        """)
        
        st.header("📊 Image Quality Standards")
        st.write("""
        **Acceptable Quality Ranges:**
        - **Sharpness**: ≥ 100 (Laplacian variance)
        - **Contrast**: ≥ 20 (Standard deviation)
        - **Brightness**: 20-235 (Mean pixel value)
        - **Dark pixels**: < 70% of image
        - **Bright pixels**: < 70% of image
        - **Overall Quality Score**: ≥ 40/100
        
        Images below these thresholds will be rejected for analysis.
        """)
        
        st.header("⚙️ Settings")
        st.write(f"""
        **Recommended Threshold:** 0.40
        
        The threshold determines when an image is classified as pneumonia. 
        - Lower values (0.3-0.4): More sensitive, fewer missed cases
        - Higher values (0.5-0.7): More specific, fewer false alarms
        """)
        
        decision_threshold = st.slider(
            "Decision Threshold",
            min_value=0.0,
            max_value=1.0,
            value=float(decision_threshold),
            step=0.05,
            help="Adjust the threshold for classification. Recommended: 0.40"
        )
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a chest X-ray image...",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a chest X-ray image in JPG or PNG format"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            img = Image.open(uploaded_file)
            st.image(img, caption='Uploaded X-ray Image', use_container_width=True)
        
        # Validate image quality first
        st.markdown("---")
        st.subheader("🔍 Image Quality Check")
        
        with st.spinner("Checking image quality..."):
            is_valid, message, quality_score = validate_image_quality(img)
        
        # Display quality score
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(quality_score / 100)
        with col2:
            color = "🟢" if quality_score >= 70 else "🟡" if quality_score >= 40 else "🔴"
            st.metric("Quality", f"{color} {quality_score:.0f}/100")
        
        # Show detailed metrics
        with st.expander("📈 View Detailed Quality Metrics"):
            img_array = np.array(img.convert('L'))
            laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()
            brightness = np.mean(img_array)
            contrast = np.std(img_array)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sharpness", f"{laplacian_var:.1f}", 
                         "✅ Pass" if laplacian_var >= 100 else "❌ Fail")
            with col2:
                st.metric("Contrast", f"{contrast:.1f}",
                         "✅ Pass" if contrast >= 20 else "❌ Fail")
            with col3:
                st.metric("Brightness", f"{brightness:.1f}",
                         "✅ Pass" if 20 <= brightness <= 235 else "❌ Fail")
            
            st.info("""
            **Quality Thresholds:**
            - Sharpness ≥ 100 (measures image focus)
            - Contrast ≥ 20 (measures detail visibility)
            - Brightness: 20-235 (proper exposure)
            """)
        
        if not is_valid:
            st.error(f"⚠️ **Image Quality Issues Detected:**\n\n{message}")
            st.warning("""
            **Please upload a clearer X-ray image for accurate analysis.**
            
            **Tips for better image quality:**
            - Ensure the image is in focus and not blurry (Sharpness ≥ 100)
            - Use proper lighting - not too dark or too bright (Brightness: 20-235)
            - Ensure good contrast for detail visibility (Contrast ≥ 20)
            - Avoid images with too much noise or artifacts
            - Make sure the X-ray is properly exposed (< 70% dark/bright pixels)
            
            **Current image did not meet the minimum quality standards for reliable analysis.**
            """)
            st.stop()  # Stop processing if image is invalid
        else:
            st.success(f"✅ {message} - Image is suitable for analysis")
        
        # Predict button
        if st.button("🔍 Analyze X-ray", use_container_width=True):
            with st.spinner("Analyzing image..."):
                # Make prediction
                pred_value = predict_image(model, img, decision_threshold)
                
                # Display results
                st.markdown("---")
                st.subheader("📊 Results")
                
                # Confidence bars
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("NORMAL", f"{(1-pred_value)*100:.1f}%")
                with col2:
                    st.metric("PNEUMONIA", f"{pred_value*100:.1f}%")
                
                # Progress bar
                st.progress(float(pred_value))
                
                # Final prediction
                if pred_value >= decision_threshold:
                    st.markdown(f"""
                    <div class="result-box pneumonia">
                        <h2>⚠️ PNEUMONIA DETECTED</h2>
                        <p style="font-size: 1.1rem;">Confidence: {pred_value*100:.2f}%</p>
                        <p style="font-size: 0.9rem; color: #721c24;">Please consult a healthcare professional for proper diagnosis.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-box normal">
                        <h2>✅ NORMAL</h2>
                        <p style="font-size: 1.1rem;">Confidence: {(1-pred_value)*100:.2f}%</p>
                        <p style="font-size: 0.9rem; color: #155724;">No signs of pneumonia detected in this X-ray.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Disclaimer
                st.info("⚕️ **Disclaimer:** This is an AI-assisted tool and should not replace professional medical diagnosis. Always consult with a qualified healthcare provider.")

if __name__ == "__main__":
    main()

    
 
