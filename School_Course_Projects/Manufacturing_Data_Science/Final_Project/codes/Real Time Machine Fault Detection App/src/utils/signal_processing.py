import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis
from scipy.signal import stft

def extract_stat_features(signal):
    return {
        'mean': np.mean(signal),
        'std': np.std(signal),
        'max': np.max(signal),
        'min': np.min(signal),
        'rms': np.sqrt(np.mean(signal**2)),
        'skewness': skew(signal),
        'kurtosis': kurtosis(signal),
        'crest_factor': np.max(np.abs(signal)) / np.sqrt(np.mean(signal**2))
    }

def compute_rotation_frequency(tachometer_signal, fs):
    N = len(tachometer_signal)
    fft_result = np.fft.fft(tachometer_signal)
    fft_magnitude = np.abs(fft_result[:N // 2])
    freqs = np.fft.fftfreq(N, d=1/fs)[:N // 2]
    peak_idx = np.argmax(fft_magnitude)
    fr = freqs[peak_idx]
    return fr

def extract_stft_features(signal, fs, fr):
    freqs, _, Zxx = stft(signal, fs=fs, nperseg=4096)
    mag = np.abs(Zxx)
    
    fr_indices = [np.argmin(np.abs(freqs - f)) for f in [fr, 2*fr, 3*fr]]

    features = {}
    for i, idx in enumerate(fr_indices):
        features[f'fr_{i+1}_mean'] = np.mean(mag[idx, :])
    
    return features

def process_signals(signals, fs=50000):
    all_features = []

    combined_features = {}
    tachometer_signal = signals[0]
    fr = compute_rotation_frequency(tachometer_signal, fs)
    combined_features['fr'] = fr
    
    for channel_idx in range(signals.shape[0]):
        signal = signals[channel_idx]
        stat_features = extract_stat_features(signal)
        for key, value in stat_features.items():
            combined_features[f'channel_{channel_idx}_{key}'] = value
        
        if channel_idx != 0:
            stft_features = extract_stft_features(signal, fs, fr)
            for key, value in stft_features.items():
                combined_features[f'channel_{channel_idx}_{key}'] = value
    
    all_features.append(combined_features)

    top_features = ['channel_1_max', 'channel_2_kurtosis', 'channel_7_skewness', 'channel_1_std',
            'channel_7_mean', 'channel_1_rms', 'channel_7_fr_1_mean', 'channel_7_fr_2_mean',
            'channel_2_crest_factor', 'channel_3_skewness', 'channel_5_max', 'channel_7_min',
            'channel_6_fr_2_mean', 'channel_4_fr_2_mean', 'channel_3_kurtosis', 'channel_1_min',
            'channel_2_rms', 'channel_2_mean', 'channel_6_fr_1_mean', 'channel_5_skewness',
            'channel_5_rms', 'channel_3_min']

    return pd.DataFrame(all_features, columns=top_features)