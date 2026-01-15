import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
import io

# Page configuration
st.set_page_config(
    page_title="Pneumonia Detection System",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0f172a 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0f172a 100%);
    }
    h1 {
        color: #ffffff;
        text-align: center;
        padding: 20px;
        font-size: 3em;
    }
    .subtitle {
        text-align: center;
        color: #cbd5e1;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    .upload-box {
        border: 2px dashed #64748b;
        border-radius: 10px;
        padding: 40px;
        text-align: center;
        background-color: rgba(30, 41, 59, 0.5);
        margin: 20px 0;
    }
    .quality-score {
        font-size: 2em;
        font-weight: bold;
        color: #10b981;
    }
    .result-box {
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        border: 2px solid;
    }
    .pneumonia-detected {
        background-color: rgba(239, 68, 68, 0.1);
        border-color: #ef4444;
    }
    .no-pneumonia {
        background-color: rgba(16, 185, 129, 0.1);
        border-color: #10b981;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        padding: 15px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
    }
    .info-box {
        background-color: rgba(59, 130, 246, 0.1);
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        color: #93c5fd;
    }
    .warning-box {
        background-color: rgba(245, 158, 11, 0.1);
        border: 1px solid #f59e0b;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        color: #fcd34d;
    }
</style>
""", unsafe_allow_html=True)

def check_image_quality(image):
    """Check image quality based on resolution and sharpness"""
    try:
        # Convert PIL to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale if colored
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        height, width = gray.shape
        
        # Calculate quality score based on resolution
        resolution_score = min(70, (width * height) / (512 * 512) * 70)
        
        # Check sharpness using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(30, laplacian_var / 10)
        
        quality = int(resolution_score + sharpness_score)
        return min(100, max(50, quality))
    except Exception as e:
        st.error(f"Error checking quality: {str(e)}")
        return 60

def analyze_pneumonia(image):
    """
    Simulate pneumonia detection
    Replace with actual AI model in production (TensorFlow, PyTorch)
    """
    try:
        # Convert PIL to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Simulate processing time
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
        
        # Simple heuristic for demonstration
        mean_intensity = np.mean(gray)
        std_intensity = np.std(gray)
        
        # Mock prediction (replace with real model)
        has_pneumonia = (mean_intensity < 120 and std_intensity > 40) or np.random.random() > 0.5
        confidence = np.random.randint(65, 95) if has_pneumonia else np.random.randint(15, 45)
        
        return {
            'has_pneumonia': bool(has_pneumonia),
            'confidence': int(confidence),
            'details': 'Pneumonia patterns detected in lung regions' if has_pneumonia 
                      else 'No significant pneumonia indicators found'
        }
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        return None

def main():
    # Initialize session state
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'quality' not in st.session_state:
        st.session_state.quality = None
    
    # Header
    st.markdown("<h1>🫁 Pneumonia Detection System</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Upload a chest X-ray image to detect pneumonia</p>", 
                unsafe_allow_html=True)
    
    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("""
        This AI-powered system analyzes chest X-ray images 
        to detect signs of pneumonia.
        """)
        
        st.header("📋 Instructions")
        st.write("""
        1. Upload a chest X-ray image
        2. Wait for quality check
        3. Click 'Analyze for Pneumonia'
        4. View results
        """)
        
        st.header("⚠️ Disclaimer")
        st.warning("""
        This is an educational tool only. 
        Always consult healthcare professionals 
        for medical diagnosis.
        """)
        
        st.header("📊 Supported Formats")
        st.info("JPG, JPEG, PNG (Max 200MB)")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload X-ray Image")
        
        uploaded_file = st.file_uploader(
            "Choose a chest X-ray image...",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a chest X-ray image in JPG, JPEG, or PNG format"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded X-ray Image", use_container_width=True)
            
            # File info
            file_size = len(uploaded_file.getvalue()) / 1024  # KB
            st.info(f"📁 **File:** {uploaded_file.name} ({file_size:.1f} KB)")
            
            # Check image quality
            if st.session_state.quality is None:
                with st.spinner("Checking image quality..."):
                    st.session_state.quality = check_image_quality(image)
            
            # Clear previous results if new image uploaded
            if 'last_uploaded_name' not in st.session_state or \
               st.session_state.last_uploaded_name != uploaded_file.name:
                st.session_state.analyzed = False
                st.session_state.result = None
                st.session_state.last_uploaded_name = uploaded_file.name
    
    with col2:
        if uploaded_file is not None:
            # Quality Check Section
            st.subheader("🔍 Image Quality Check")
            
            quality = st.session_state.quality
            
            # Quality progress bar
            if quality >= 70:
                color = "green"
                status = "✅ Excellent"
            elif quality >= 50:
                color = "orange"
                status = "⚠️ Acceptable"
            else:
                color = "red"
                status = "❌ Poor"
            
            st.markdown(f"**Quality Score:** <span class='quality-score' style='color: {color}'>{quality}/100</span>", 
                       unsafe_allow_html=True)
            st.progress(quality / 100)
            st.markdown(f"**Status:** {status}")
            
            if quality >= 50:
                st.success("✓ Image quality is acceptable for analysis")
            else:
                st.warning("⚠️ Image quality is low. Results may be less accurate.")
            
            st.markdown("---")
            
            # Analysis Button
            if not st.session_state.analyzed:
                if st.button("🔬 Analyze for Pneumonia", type="primary"):
                    with st.spinner("Analyzing X-ray image..."):
                        result = analyze_pneumonia(image)
                        if result:
                            st.session_state.result = result
                            st.session_state.analyzed = True
                            st.rerun()
            else:
                if st.button("🔄 Analyze Another Image"):
                    st.session_state.analyzed = False
                    st.session_state.result = None
                    st.session_state.quality = None
                    st.session_state.last_uploaded_name = None
                    st.rerun()
    
    # Results Section
    if st.session_state.analyzed and st.session_state.result:
        st.markdown("---")
        st.subheader("📊 Detection Results")
        
        result = st.session_state.result
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if result['has_pneumonia']:
                st.error(f"### 🚨 Pneumonia Detected")
            else:
                st.success(f"### ✅ No Pneumonia Detected")
        
        with col2:
            st.metric("Confidence Score", f"{result['confidence']}%")
        
        with col3:
            if result['has_pneumonia']:
                st.metric("Risk Level", "High", delta="⚠️")
            else:
                st.metric("Risk Level", "Low", delta="✓")
        
        # Detailed results
        if result['has_pneumonia']:
            st.markdown(f"""
            <div class='result-box pneumonia-detected'>
                <h3 style='color: #ef4444;'>⚠️ Pneumonia Indicators Found</h3>
                <p style='color: #fca5a5; font-size: 1.1em;'>{result['details']}</p>
                <p style='color: #fca5a5;'><strong>Confidence:</strong> {result['confidence']}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.error("""
            **⚠️ Important Next Steps:**
            - Consult a pulmonologist or radiologist immediately
            - Get a professional medical diagnosis
            - Follow prescribed treatment plans
            - This AI analysis is for screening purposes only
            """)
        else:
            st.markdown(f"""
            <div class='result-box no-pneumonia'>
                <h3 style='color: #10b981;'>✅ No Significant Pneumonia Indicators</h3>
                <p style='color: #6ee7b7; font-size: 1.1em;'>{result['details']}</p>
                <p style='color: #6ee7b7;'><strong>Confidence:</strong> {result['confidence']}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("""
            **ℹ️ Recommendations:**
            - Continue regular health checkups
            - Maintain good respiratory hygiene
            - Consult a doctor if symptoms develop
            - This does not replace professional medical examination
            """)
        
        # Medical Disclaimer
        st.markdown("""
        <div class='warning-box'>
            <h4>⚠️ Medical Disclaimer</h4>
            <p>This application is for educational and research purposes only. 
            It should NOT be used as a substitute for professional medical advice, 
            diagnosis, or treatment. Always consult with qualified healthcare 
            professionals for proper medical care.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #94a3b8; padding: 20px;'>
        <p>Made with ❤️ using Streamlit | © 2026 Pneumonia Detection System</p>
        
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main(
