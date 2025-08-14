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
        self.voice_model_id = None
        self.voice_style_id = None
        self.audio_output = None

    def set_voice_model(self, voice_model_id: int):
        """Set the voice model to use for synthesis.
        Args:
            voice_model_id (int): The index of the voice model to set.
        """
        self.voice_model_id = voice_model_id
        with VoiceModelFile.open(f'./src/voicevox/python/models/vvms/{self.voice_model_id}.vvm') as model:
            self.synthesizer.load_voice_model(model)
        print(f"Voice model set to {self.voice_model_id}.")
        
    def list_styles(self):
        """List available styles for the current voice model.
        Meta example:
        CharacterMeta(name='四国めたん',
               styles=[StyleMeta(name='ノーマル', id=2, type='talk', order=0),
                       StyleMeta(name='あまあま', id=0, type='talk', order=1),
                       StyleMeta(name='ツンツン', id=6, type='talk', order=2),
                       StyleMeta(name='セクシー', id=4, type='talk', order=3)],
               speaker_uuid='7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff',
               version='0.1.0',
               order=0)
        """
        style_metas = self.synthesizer.metas()
        style_id_info = []
        for style in style_metas:
            voice_actor_name = style.name
            for sub_style_meta in style.styles:
                style_id_info.append({
                    "id": sub_style_meta.id,
                    "actor_name": voice_actor_name,
                    "style_name": sub_style_meta.name
                })
        return style_id_info
    
    def set_voice_style(self, voice_style_id):
        """Set the voice style for synthesis.
        Args:
            style_id (int): The ID of the style to set.
        """
        self.voice_style_id = voice_style_id
        print(f"Voice style set to {self.voice_style_id}.")

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech from text using the loaded voice model and style ID.
        Args:
            text (str): The text to synthesize.
            style_id (int): The style ID for the synthesis.
        Returns:
            bytes: The synthesized audio data in WAV format.
        """
        print(f"voice_model_id: {self.voice_model_id}, voice_style_id: {self.voice_style_id}")
        if self.voice_style_id is None or self.voice_model_id is None:
            raise ValueError("Voice model/style must be set before synthesis.")
        audio_query = self.synthesizer.create_audio_query(
            text,
            style_id=self.voice_style_id
        )
        wav = self.synthesizer.synthesis(
            audio_query,
            style_id=self.voice_style_id
        )
        self.audio_output = wav

    def write_wav_to_file(self, filename: str):
        """Write the synthesized WAV data to a file.
        
        Args:
            filename (str): The name of the file to write the WAV data to.
        """
        if not os.path.exists('./media'):
            os.makedirs('./media')
        if not self.audio_output:
            raise ValueError("No audio output available to write.")
        with open(f"./media/{filename}", 'wb') as f:
            f.write(self.audio_output)
        print(f"WAV data written to {filename}.")
