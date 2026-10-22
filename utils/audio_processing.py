import os
import librosa
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import cosine

def preprocess_audio(audio_path, target_sr=22050):
    """Loads audio, converts to mono, resamples, and trims silence."""
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        raise ValueError(f"Audio file '{audio_path}' is empty or does not exist.")
        
    y, sr = librosa.load(audio_path, sr=target_sr, mono=True)
    # Trim leading/trailing silence (top_db=25 removes quiet room noise)
    y_trimmed, _ = librosa.effects.trim(y, top_db=25)
    return y_trimmed, sr

def extract_features(y, sr, n_mfcc=13):
    """
    Extracts standard 13 MFCC features with Cepstral Mean & Variance Normalization (CMVN).
    """
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    
    # Apply Cepstral Mean and Variance Normalization
    mean = np.mean(mfcc, axis=1, keepdims=True)
    std = np.std(mfcc, axis=1, keepdims=True) + 1e-8
    normalized_mfcc = (mfcc - mean) / std
    
    return {
        "mfcc": normalized_mfcc
    }

def calculate_similarity(ref_features, student_features):
    """
    Calculates DTW distance using Cosine distance and applies a 
    piecewise calibration curve to account for human microphone differences.
    """
    ref_mfcc = ref_features["mfcc"].T
    student_mfcc = student_features["mfcc"].T
    
    # FastDTW using COSINE distance
    distance, _ = fastdtw(ref_mfcc, student_mfcc, dist=cosine)
    norm_distance = distance / (len(ref_mfcc) + len(student_mfcc))
    
    # Piecewise Score Mapping:
    if norm_distance <= 0.05:
        # Identical or near-identical digital file match (100% -> 95%)
        score = 100.0 - (norm_distance / 0.05) * 5.0
    elif norm_distance <= 0.40:
        # Good human recording with natural mic/timbre differences (95% -> 68%)
        score = 95.0 - ((norm_distance - 0.05) / 0.35) * 27.0
    elif norm_distance <= 0.60:
        # Moderate attempt with mispronunciation or timing mismatch (68% -> 35%)
        score = 68.0 - ((norm_distance - 0.40) / 0.20) * 33.0
    else:
        # Wrong word or noise (>0.60 -> 0%)
        score = max(0.0, 35.0 - ((norm_distance - 0.60) / 0.20) * 35.0)
    
    return round(score, 2), norm_distance