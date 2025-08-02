from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
import os

class TextToSpeechHandler:
    def __init__(self):
        self.onnxruntime = Onnxruntime.load_once(
            filename='./src/voicevox/python/onnxruntime/lib/libvoicevox_onnxruntime.so.1.17.3'
        )
        self.synthesizer = Synthesizer(
            self.onnxruntime,
            OpenJtalk(
                './src/voicevox/python/dict/open_jtalk_dic_utf_8-1.11'
            ),
        acceleration_mode='AUTO',
        cpu_num_threads=4
    )
        self.voice_model_number = 0
        with VoiceModelFile.open(f'./src/voicevox/python/models/vvms/{self.voice_model_number}.vvm') as model:
            self.synthesizer.load_voice_model(model)
            
    def synthesize(self, text: str, style_id: int = 0) -> bytes:
        """        Synthesize speech from text using the loaded voice model and style ID.
        Args:
            text (str): The text to synthesize.
            style_id (int): The style ID for the synthesis.
        Returns:
            bytes: The synthesized audio data in WAV format.
        """
        styles = self.synthesizer.metas()
        if style_id < 0 or style_id >= len(styles):
            raise ValueError(f"Invalid style_id: {style_id}. Must be between 0 and {len(styles) - 1}.")
        audio_query = self.synthesizer.create_audio_query(
            text,
            style_id=style_id
        )
        wav = self.synthesizer.synthesis(
            audio_query,
            style_id=style_id
        )
        return wav
    
    def list_styles(self):
        """List available styles for the current voice model."""
        styles = self.synthesizer.metas()
        return [style.name for style in styles]
    
    def set_voice_model(self, voice_model_number: int):
        """Set the voice model to use for synthesis.
        
        Args:
            voice_model_number (int): The index of the voice model to set.
        """
        self.voice_model_number = voice_model_number
        with VoiceModelFile.open(f'./src/voicevox/python/models/vvms/{self.voice_model_number}.vvm') as model:
            self.synthesizer.load_voice_model(model)
        print(f"Voice model set to {self.voice_model_number}.")
    
    def write_wav_to_file(self, wav: bytes, filename: str):
        """Write the synthesized WAV data to a file.
        
        Args:
            wav (bytes): The synthesized audio data in WAV format.
            filename (str): The name of the file to write the WAV data to.
        """
        if not os.path.exists('../media'):
            os.makedirs('../media')
        with open(f"../media/{filename}", 'wb') as f:
            f.write(wav)
        print(f"WAV data written to {filename}.")
        