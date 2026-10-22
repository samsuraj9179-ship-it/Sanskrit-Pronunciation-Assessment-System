import os
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from utils.audio_processing import preprocess_audio, extract_features, calculate_similarity
from utils.visualization import plot_comparison

# Page Configuration - Start with Sidebar Expanded
st.set_page_config(
    page_title="Sanskrit Pronunciation Assessor",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 1. FIXED UI: TRANSPARENT TEXT BOXES, ICONS & ANIMATED BACKGROUND
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* --- 1. IMPORT FONTS & MATERIAL ICONS --- */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Yatra+One&family=Tiro+Devanagari+Sanskrit:ital@0;1&family=Cinzel:wght@500;700;800&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

    /* --- 2. BASE APP BACKGROUND --- */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        background-color: #0a0d12 !important;
    }

    /* --- 3. WIPE OUT ALL DARK HIGHLIGHT BOXES BEHIND TEXT --- */
    .stMarkdown, .stMarkdown p, .stMarkdown span, 
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span,
    [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, label,
    div[data-testid="stAlert"] > div, div[data-testid="stAlert"] p,
    .glass-card p, .glass-card span {
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }

    /* --- 4. APPLY MYTHICAL TYPOGRAPHY (Targeted safely to avoid breaking icons) --- */
    p, label, li, div[data-baseweb="select"] * {
        font-family: 'Tiro Devanagari Sanskrit', serif !important;
    }
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Cinzel', 'Yatra One', serif !important;
        letter-spacing: 1px;
    }

    /* --- 5. PROTECT & RESTORE ALL ARROW ICONS --- */
    .stIcon, span[class*="material-symbols"], i[class*="material-icons"],
    [data-testid="stSidebarCollapsedControl"] *,
    [data-testid="stSidebarCollapseButton"] * {
        font-family: 'Material Symbols Rounded', sans-serif !important;
    }

    /* --- 6. ANIMATED SANSKRIT PARTICLES --- */
    .sanskrit-bg-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
        background: radial-gradient(circle at 50% 20%, #1f140a 0%, #0a0d12 75%);
    }

    .sanskrit-particle {
        position: absolute;
        bottom: -80px;
        font-family: 'Yatra One', 'Tiro Devanagari Sanskrit', serif !important;
        font-weight: 400;
        color: rgba(255, 153, 51, 0.35);
        text-shadow: 0 0 18px rgba(255, 153, 51, 0.5);
        animation: floatUp linear infinite;
    }

    @keyframes floatUp {
        0% { transform: translateY(0) rotate(0deg); opacity: 0; }
        20% { opacity: 0.6; }
        80% { opacity: 0.6; }
        100% { transform: translateY(-115vh) rotate(20deg); opacity: 0; }
    }

    [data-testid="stVerticalBlock"], .glass-card {
        position: relative;
        z-index: 1;
    }

    /* --- 7. MAIN TITLES & CALLIGRAPHY --- */
    p.main-header {
        font-family: 'Cinzel Decorative', 'Yatra One', serif !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        background: linear-gradient(90deg, #FF9933 0%, #FFA726 50%, #FFD54F 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 0.2rem !important;
        text-shadow: 0 0 25px rgba(255, 153, 51, 0.4) !important;
        display: inline-block !important;
    }

    p.sub-header {
        font-family: 'Tiro Devanagari Sanskrit', serif !important;
        font-size: 1.1rem !important;
        color: #94a3b8 !important;
        margin-bottom: 1.2rem !important;
    }

    .devanagari-title {
        font-family: 'Yatra One', 'Tiro Devanagari Sanskrit', serif !important;
        font-size: 3.5rem;
        color: #FFB74D;
        margin: 0;
        text-shadow: 0 0 30px rgba(255, 183, 77, 0.65);
    }

    .iast-sub {
        font-family: 'Tiro Devanagari Sanskrit', serif !important;
        font-size: 1.25rem;
        color: #cbd5e1;
        font-style: italic;
    }

    /* --- 8. GLASSMORPHISM PANELS & ALERTS --- */
    .glass-card {
        background: rgba(22, 27, 34, 0.65) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid rgba(255, 183, 77, 0.3) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6), inset 0 0 15px rgba(255, 153, 51, 0.1) !important;
        padding: 22px !important;
        margin-bottom: 20px !important;
        text-align: center;
    }

    [data-testid="stAlert"] {
        background: rgba(22, 27, 34, 0.45) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(255, 183, 77, 0.25) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* --- 9. DROPDOWN (Selectbox) STYLING --- */
    div[data-baseweb="select"] > div {
        background-color: rgba(18, 22, 30, 0.8) !important;
        border: 1px solid rgba(255, 183, 77, 0.4) !important;
        border-radius: 8px !important;
    }

    /* --- 10. SIDEBAR ARROW TOGGLE BUTTON --- */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        background: rgba(22, 27, 34, 0.95) !important;
        border: 2px solid #FFB74D !important;
        border-radius: 50% !important;
        box-shadow: 0 0 15px rgba(255, 183, 77, 0.5) !important;
        transition: transform 0.2s ease !important;
        z-index: 999999 !important;
    }

    [data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="stSidebarCollapseButton"]:hover {
        transform: scale(1.12) !important;
        box-shadow: 0 0 25px rgba(255, 183, 77, 0.9) !important;
    }

    [data-testid="stSidebarCollapsedControl"] svg, 
    [data-testid="stSidebarCollapseButton"] svg {
        fill: #FFB74D !important;
        color: #FFB74D !important;
    }

    /* --- 11. SIDEBAR PANEL --- */
    [data-testid="stSidebar"] {
        background: rgba(18, 22, 30, 0.82) !important;
        backdrop-filter: blur(24px) saturate(190%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(190%) !important;
        border-right: 1px solid rgba(255, 183, 77, 0.35) !important;
        box-shadow: 10px 0 35px rgba(0, 0, 0, 0.7) !important;
        z-index: 99999 !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding-top: 3.5rem !important;
    }

    /* --- 12. MICROPHONE WIDGET CONSTRAINT --- */
    div[data-testid="stCustomComponentV1"] {
        display: inline-block !important;
        width: 75px !important;
        background: transparent !important;
    }

    iframe[title="audio_recorder_streamlit.audio_recorder"] {
        width: 75px !important;
        height: 75px !important;
        min-width: 75px !important;
        border-radius: 12px !important;
        background: transparent !important;
        overflow: hidden !important;
    }
</style>

<!-- Animated Floating Sanskrit Particles -->
<div class="sanskrit-bg-overlay">
    <div class="sanskrit-particle" style="left: 4%; font-size: 2.8rem; animation-duration: 10s; animation-delay: 0s;">ॐ</div>
    <div class="sanskrit-particle" style="left: 14%; font-size: 2.0rem; animation-duration: 14s; animation-delay: 2s;">कृष्ण</div>
    <div class="sanskrit-particle" style="left: 26%; font-size: 3.0rem; animation-duration: 9s; animation-delay: 1s;">ऋ</div>
    <div class="sanskrit-particle" style="left: 38%; font-size: 2.2rem; animation-duration: 12s; animation-delay: 4s;">राम</div>
    <div class="sanskrit-particle" style="left: 50%; font-size: 2.1rem; animation-duration: 11s; animation-delay: 1.5s;">गच्छति</div>
    <div class="sanskrit-particle" style="left: 62%; font-size: 2.5rem; animation-duration: 13s; animation-delay: 3s;">नमस्ते</div>
    <div class="sanskrit-particle" style="left: 74%; font-size: 3.2rem; animation-duration: 8.5s; animation-delay: 0.5s;">ॐ</div>
    <div class="sanskrit-particle" style="left: 86%; font-size: 2.0rem; animation-duration: 15s; animation-delay: 5s;">ज्ञानम्</div>
    <div class="sanskrit-particle" style="left: 20%; font-size: 2.3rem; animation-duration: 11.5s; animation-delay: 6s;">सत्यम्</div>
    <div class="sanskrit-particle" style="left: 58%; font-size: 2.7rem; animation-duration: 10.5s; animation-delay: 2.5s;">अ</div>
    <div class="sanskrit-particle" style="left: 92%; font-size: 2.2rem; animation-duration: 13.5s; animation-delay: 1s;">क</div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. APPLICATION CONTENT & LOGIC
# -----------------------------------------------------------------------------

# Header
st.markdown('<p class="main-header">🎙️ Sanskrit Pronunciation Assessment System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Acoustic Speech Analysis Engine using MFCC & Dynamic Time Warping (DTW)</p>', unsafe_allow_html=True)

# Master Dictionary
SANSKRIT_WORDS = {
    "Krishna — कृष्ण (kṛṣṇa)": {
        "file": "krishna_ref",
        "devanagari": "कृष्ण",
        "iast": "kṛṣṇa",
        "meaning": "Dark / All-attractive"
    },
    "Rama — राम (rāma)": {
        "file": "rama_ref",
        "devanagari": "राम",
        "iast": "rāma",
        "meaning": "Pleasing / Delightful"
    },
    "Namaste — नमस्ते (namaste)": {
        "file": "namaste_ref",
        "devanagari": "नमस्ते",
        "iast": "namaste",
        "meaning": "I bow to you"
    },
    "Gacchati — गच्छति (gacchati)": {
        "file": "gacchati_ref",
        "devanagari": "गच्छति",
        "iast": "gacchati",
        "meaning": "Goes / Walking"
    }
}

# TOGGLEABLE SIDEBAR MENU
st.sidebar.markdown("### ⚙️ Target Word")
st.sidebar.markdown("Search or pick a Sanskrit word:")

selected_label = st.sidebar.selectbox(
    "Select Word:",
    options=list(SANSKRIT_WORDS.keys()),
    label_visibility="collapsed"
)

word_info = SANSKRIT_WORDS[selected_label]
file_base = word_info["file"]

# Auto-detect reference file extension (.mp3 or .wav)
REF_PATH = f"audio_reference/{file_base}.mp3"
if not os.path.exists(REF_PATH):
    REF_PATH = f"audio_reference/{file_base}.wav"

st.sidebar.markdown("---")
st.sidebar.markdown("**Technical Specs:**")
st.sidebar.info("""
• **Feature Engine:** MFCC (13 coefficients)
• **Alignment:** FastDTW (Cosine Distance)
• **Normalization:** CMVN Filtered
""")

# Main Layout: 2 Columns
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown("### Target Pronunciation")
    
    # Target Word Glassmorphism Banner
    st.markdown(f"""
    <div class="glass-card">
        <p class="devanagari-title">{word_info['devanagari']}</p>
        <p class="iast-sub">IAST: <b>{word_info['iast']}</b> | Meaning: <i>{word_info['meaning']}</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Reference Audio Player
    if os.path.exists(REF_PATH):
        st.write("📢 **Reference Native Audio:**")
        st.audio(REF_PATH)
    else:
        st.error(f"⚠️ Missing reference file: `audio_reference/{file_base}.mp3`")

    st.markdown("---")
    st.markdown("### Student Audio Input")
    
    input_mode = st.radio(
        "Choose Input Method:",
        ("🎙️ Live Microphone", "📁 Upload File"),
        horizontal=True
    )
    
    student_audio_path = None
    
    if input_mode == "🎙️ Live Microphone":
        st.write("Click mic icon to record:")
        audio_bytes = audio_recorder(
            text="",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_size="3x"
        )
        if audio_bytes:
            student_audio_path = "temp_student.wav"
            with open(student_audio_path, "wb") as f:
                f.write(audio_bytes)
                
    elif input_mode == "📁 Upload File":
        uploaded_file = st.file_uploader("Upload WAV or MP3 audio:", type=["wav", "mp3"])
        if uploaded_file is not None:
            ext = uploaded_file.name.split(".")[-1]
            student_audio_path = f"temp_student.{ext}"
            with open(student_audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

    if student_audio_path:
        st.write("🎧 **Recorded Student Input:**")
        st.audio(student_audio_path)

with col_right:
    st.markdown("### Acoustic Assessment Results")
    
    if student_audio_path and os.path.exists(REF_PATH):
        with st.spinner("Extracting MFCC features & computing FastDTW alignment..."):
            y_ref, sr_ref = preprocess_audio(REF_PATH)
            y_stud, sr_stud = preprocess_audio(student_audio_path)
            
            ref_feat = extract_features(y_ref, sr_ref)
            stud_feat = extract_features(y_stud, sr_stud)
            
            score, distance = calculate_similarity(ref_feat, stud_feat)
            
            # Metrics Dashboard
            m1, m2 = st.columns(2)
            m1.metric("Pronunciation Accuracy", f"{score}%")
            m2.metric("Normalized DTW Distance", f"{round(distance, 4)}")
            
            # Progress Bar Score Display
            st.progress(int(score) / 100)
            
            # Diagnostic Feedback Callout
            if score >= 80:
                st.success("🌟 **Excellent Pronunciation!** High acoustic spectral alignment and accurate phoneme duration.")
            elif score >= 60:
                st.warning("⚠️ **Good Attempt (Minor Deviation):** Check retroflex consonant emphasis or vowel length (*Mātrā*).")
            else:
                st.error("❌ **Significant Mismatch Detected:** Inaccurate vocal timbre or wrong word spoken.")
                
            # Tabbed Visualizations
            tab1, tab2 = st.tabs(["📊 Acoustic Feature Plots", "📋 Detailed Metrics Breakdown"])
            
            with tab1:
                fig = plot_comparison(y_ref, sr_ref, ref_feat["mfcc"], y_stud, sr_stud, stud_feat["mfcc"])
                st.pyplot(fig)
                
            with tab2:
                st.write("**Technical Parameter Breakdown:**")
                st.json({
                    "Target Word": word_info["iast"],
                    "Reference Audio Sampling Rate": f"{sr_ref} Hz",
                    "Student Audio Sampling Rate": f"{sr_stud} Hz",
                    "MFCC Coefficient Count": 13,
                    "Alignment Algorithm": "FastDTW (Cosine Distance Metric)",
                    "Normalized Cost": round(distance, 5),
                    "Final Similarity Rating": f"{score}%"
                })
    else:
        st.info("👈 Provide student audio using the microphone or file uploader to generate real-time assessment.")