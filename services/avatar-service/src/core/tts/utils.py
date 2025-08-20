def file_name_to_id(filename: str) -> int:
    """Extract the model ID from the filename."""
    return int(filename.split('.')[0])

def create_wav_file(audio_output, wav_output_path) -> None:
    """Create a WAV file from the given audio data"""
    with open(wav_output_path, "wb") as wav_file:
        wav_file.write(audio_output)