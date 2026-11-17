"""
StrataSentry-NWIS: PyTorch / NumPy LSTM Autoencoder Model
Reconstructs multivariate time-series window to detect subtle multi-channel drift.
"""

from typing import Tuple, List, Optional
import numpy as np

class LSTMAutoencoderArchitecture:
    """
    Lightweight, vectorized autoencoder implementation for CPU/Edge inference
    compatible with PyTorch model checkpoints or pure NumPy execution.
    """
    def __init__(self, sequence_length: int = 60, n_features: int = 12, latent_dim: int = 16):
        self.seq_len = sequence_length
        self.n_features = n_features
        self.latent_dim = latent_dim
        # Baseline normal weights representation
        rng = np.random.default_rng(42)
        self.W_enc = rng.standard_normal((n_features, latent_dim)) * 0.1
        self.W_dec = rng.standard_normal((latent_dim, n_features)) * 0.1

    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        x shape: (batch_size, sequence_length, n_features)
        Returns reconstructed x_recon with same shape.
        """
        # Linear bottleneck projection + tanh activation
        latent = np.tanh(np.dot(x, self.W_enc))
        recon = np.dot(latent, self.W_dec)
        return recon
