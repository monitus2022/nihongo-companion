import soundfile as sf
import numpy as np
import librosa
import resampy
from io import BytesIO
from typing import List, Tuple, Optional

from utils import avatar_service_logger as logger
from config import config


class AudioProcessor:
    """
    Audio processing pipeline for lip-sync video generation.
    Handles TTS audio preprocessing, chunking, and mel-spectrogram conversion.
    """

    def __init__(
        self,
        target_sample_rate: int = 16000,
        chunk_duration_ms: int = 20,
        mel_bands: int = 80,
    ):
        """
        Initialize audio processor with configuration.

        Args:
            target_sample_rate: Target sample rate for processing (16kHz for Wav2Lip)
            chunk_duration_ms: Duration of each audio chunk in milliseconds
            mel_bands: Number of mel-frequency bands for spectrogram
        """
        self.target_sample_rate = target_sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.mel_bands = mel_bands

        # Calculated properties
        self.chunk_size = int(
            target_sample_rate * chunk_duration_ms / 1000
        )  # 320 samples
        self.hop_length = int(self.chunk_size / 2)  # 160 for 4 time steps

        # State
        self._raw_audio: Optional[np.ndarray] = None
        self._processed_audio: Optional[np.ndarray] = None
        self._audio_chunks: Optional[List[np.ndarray]] = None
        self._mel_features: Optional[List[np.ndarray]] = None

    def load_from_binary(self, audio_binary: bytes):
        """
        Load audio from binary data (e.g., from TTS output).
        """
        try:
            audio_buffer = BytesIO(audio_binary)
            audio, sample_rate = sf.read(audio_buffer)

            self._raw_audio = audio.astype(np.float32)
            self.original_sample_rate = sample_rate

            logger.info(
                f"Loaded audio: shape={audio.shape}, sr={sample_rate}Hz, "
                f"duration={len(audio)/sample_rate:.2f}s"
            )

        except Exception as e:
            logger.error(f"Failed to load audio from binary: {e}")
            raise

    def load_from_file(self, file_path: str):
        """
        Load audio from file.
        """
        try:
            audio, sample_rate = sf.read(file_path)
            self._raw_audio = audio.astype(np.float32)
            self.original_sample_rate = sample_rate

            logger.info(f"Loaded audio file: {file_path}")

        except Exception as e:
            logger.error(f"Failed to load audio file {file_path}: {e}")
            raise

    def preprocess(self):
        """
        Preprocess audio: convert to mono, resample to target rate.
        """
        if self._raw_audio is None:
            raise RuntimeError(
                "No audio loaded. Call load_from_binary() or load_from_file() first."
            )

        try:
            audio = self._raw_audio

            # Convert to mono if stereo
            if audio.ndim > 1:
                audio = np.mean(audio, axis=1)
                logger.debug("Converted stereo to mono")

            # Resample if needed
            if self.original_sample_rate != self.target_sample_rate:
                audio = resampy.resample(
                    audio, self.original_sample_rate, self.target_sample_rate
                )
                logger.debug(
                    f"Resampled from {self.original_sample_rate}Hz to {self.target_sample_rate}Hz"
                )

            self._processed_audio = audio

            logger.info(
                f"Preprocessed audio: {len(audio)} samples, "
                f"{len(audio)/self.target_sample_rate:.2f}s duration"
            )

        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            raise

    def chunk_audio(self):
        """
        Split processed audio into fixed-duration chunks.
        """
        if self._processed_audio is None:
            raise RuntimeError("No processed audio. Call preprocess() first.")

        try:
            audio = self._processed_audio
            chunks = []

            for i in range(0, len(audio), self.chunk_size):
                chunk = audio[i : i + self.chunk_size]

                # Only keep chunks that are exactly the right size
                if len(chunk) == self.chunk_size:
                    chunks.append(chunk)
                else:
                    # Pad the last chunk if it's too short
                    padded_chunk = np.pad(
                        chunk, (0, self.chunk_size - len(chunk)), "constant"
                    )
                    chunks.append(padded_chunk)

            self._audio_chunks = chunks

        except Exception as e:
            logger.error(f"Audio chunking failed: {e}")
            raise

    def generate_mel_spectrograms(self):
        """
        Convert audio chunks to mel-spectrograms for Wav2Lip.
        """
        if self._audio_chunks is None:
            raise RuntimeError("No audio chunks. Call chunk_audio() first.")

        try:
            mel_features = []

            for i, chunk in enumerate(self._audio_chunks):
                mel_spec = self._chunk_to_mel_spectrogram(chunk)
                mel_features.append(mel_spec)

                if i < 3:  # Log first few for debugging
                    logger.debug(f"Chunk {i} mel shape: {mel_spec.shape}")

            self._mel_features = mel_features

        except Exception as e:
            logger.error(f"Mel-spectrogram generation failed: {e}")
            raise

    def _chunk_to_mel_spectrogram(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
        Convert single audio chunk to mel-spectrogram.

        Args:
            audio_chunk: Audio chunk (320 samples for 20ms at 16kHz)

        Returns:
            Mel-spectrogram with shape (80, 4) for Wav2Lip
        """
        # Ensure exact chunk length
        if len(audio_chunk) < self.chunk_size:
            audio_chunk = np.pad(
                audio_chunk, (0, self.chunk_size - len(audio_chunk)), "constant"
            )
        elif len(audio_chunk) > self.chunk_size:
            audio_chunk = audio_chunk[: self.chunk_size]

        # Generate mel-spectrogram with Wav2Lip parameters
        mel_spec = librosa.feature.melspectrogram(
            y=audio_chunk,
            sr=self.target_sample_rate,
            n_mels=self.mel_bands,  # 80 mel bands
            n_fft=800,  # FFT window size
            hop_length=self.hop_length,  # 160 for 4 time steps
            win_length=800,  # Window length
            fmin=55,  # Min frequency
            fmax=7600,  # Max frequency
            center=True,
        )

        # Convert to log scale
        mel_spec = np.log(mel_spec + 1e-8)

        # Ensure exactly 4 time steps for Wav2Lip
        if mel_spec.shape[1] < 4:
            pad_width = ((0, 0), (0, 4 - mel_spec.shape[1]))
            mel_spec = np.pad(mel_spec, pad_width, mode="edge")
        elif mel_spec.shape[1] > 4:
            mel_spec = mel_spec[:, :4]

        assert mel_spec.shape == (
            self.mel_bands,
            4,
        ), f"Expected ({self.mel_bands}, 4), got {mel_spec.shape}"
        return mel_spec

    def save_processed_audio(self, output_path: str) -> None:
        """Save processed audio to file."""
        if self._processed_audio is None:
            raise RuntimeError("No processed audio to save.")

        sf.write(output_path, self._processed_audio, self.target_sample_rate)
        logger.info(f"Saved processed audio to: {output_path}")

    def process_pipeline(self, audio_binary: bytes) -> List[np.ndarray]:
        """
        Complete processing pipeline: load -> preprocess -> chunk -> mel-spectrograms.

        Args:
            audio_binary: Raw audio bytes from TTS

        Returns:
            List of mel-spectrograms ready for Wav2Lip
        """
        self.load_from_binary(audio_binary)
        self.preprocess()
        self.chunk_audio()
        self.generate_mel_spectrograms()
        return self.mel_features

    # Properties for accessing results
    @property
    def mel_features(self) -> List[np.ndarray]:
        """Get generated mel-spectrograms."""
        if self._mel_features is None:
            raise RuntimeError(
                "No mel features generated. Run the processing pipeline first."
            )
        return self._mel_features

    @property
    def audio_chunks(self) -> List[np.ndarray]:
        """Get audio chunks."""
        if self._audio_chunks is None:
            raise RuntimeError("No audio chunks generated. Call chunk_audio() first.")
        return self._audio_chunks

    @property
    def processed_audio(self) -> np.ndarray:
        """Get processed audio."""
        if self._processed_audio is None:
            raise RuntimeError("No processed audio. Call preprocess() first.")
        return self._processed_audio

    @property
    def duration_seconds(self) -> float:
        """Get audio duration in seconds."""
        if self._processed_audio is None:
            return 0.0
        return len(self._processed_audio) / self.target_sample_rate

    @property
    def chunk_count(self) -> int:
        """Get number of audio chunks."""
        return len(self._audio_chunks) if self._audio_chunks else 0


def create_audio_processor():
    """Create AudioProcessor with default Wav2Lip settings."""
    return AudioProcessor(target_sample_rate=16000, chunk_duration_ms=20, mel_bands=80)
