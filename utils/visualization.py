import matplotlib.pyplot as plt
import librosa.display
import numpy as np

def plot_comparison(y_ref, sr_ref, mfcc_ref, y_stud, sr_stud, mfcc_stud):
    """
    Generates side-by-side dark-themed acoustic plots for Waveforms, 
    Log Spectrograms, and Normalized MFCC Heatmaps.
    """
    # Set dark theme for academic presentation screenshots
    plt.style.use('dark_background')
    fig, axes = plt.subplots(3, 2, figsize=(12, 9), facecolor='#0e1117')
    
    for ax in axes.flat:
        ax.set_facecolor('#161b22')
        ax.tick_params(colors='#8b949e', labelsize=8)

    # 1. Waveform Comparison
    librosa.display.waveshow(y_ref, sr=sr_ref, ax=axes[0, 0], color='#4FC3F7', alpha=0.85)
    axes[0, 0].set_title("Reference Signal Waveform", fontsize=11, fontweight='bold', color='#E0E0E0')
    axes[0, 0].set_xlabel("")
    
    librosa.display.waveshow(y_stud, sr=sr_stud, ax=axes[0, 1], color='#FFB74D', alpha=0.85)
    axes[0, 1].set_title("Student Signal Waveform", fontsize=11, fontweight='bold', color='#E0E0E0')
    axes[0, 1].set_xlabel("")

    # 2. Log-Frequency Spectrograms
    D_ref = librosa.amplitude_to_db(np.abs(librosa.stft(y_ref)), ref=np.max)
    librosa.display.specshow(D_ref, sr=sr_ref, x_axis='time', y_axis='log', ax=axes[1, 0], cmap='magma')
    axes[1, 0].set_title("Reference Spectrogram (Energy Spectrum)", fontsize=11, fontweight='bold', color='#E0E0E0')
    axes[1, 0].set_xlabel("")

    D_stud = librosa.amplitude_to_db(np.abs(librosa.stft(y_stud)), ref=np.max)
    librosa.display.specshow(D_stud, sr=sr_stud, x_axis='time', y_axis='log', ax=axes[1, 1], cmap='magma')
    axes[1, 1].set_title("Student Spectrogram (Energy Spectrum)", fontsize=11, fontweight='bold', color='#E0E0E0')
    axes[1, 1].set_xlabel("")

    # 3. MFCC Feature Matrix
    librosa.display.specshow(mfcc_ref, x_axis='time', ax=axes[2, 0], cmap='viridis')
    axes[2, 0].set_title("Reference MFCC Matrix (13 Coefficients)", fontsize=11, fontweight='bold', color='#E0E0E0')
    axes[2, 0].set_xlabel("Time (s)", color='#8b949e', fontsize=9)

    librosa.display.specshow(mfcc_stud, x_axis='time', ax=axes[2, 1], cmap='viridis')
    axes[2, 1].set_title("Student MFCC Matrix (13 Coefficients)", fontsize=11, fontweight='bold', color='#E0E0E0')
    axes[2, 1].set_xlabel("Time (s)", color='#8b949e', fontsize=9)

    plt.tight_layout()
    return fig