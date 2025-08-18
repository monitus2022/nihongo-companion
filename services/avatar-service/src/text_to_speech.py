from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
import os
import json
from typing import Dict, List
from utils import file_name_to_id

class TextToSpeechHandler:
    def __init__(self) -> None:
        """Initialize TTS handler and optionally load voice options
        
        Args:
            load_voice_options (bool): Whether to load voice options during init
        """
        # Initialize VoiceVox components
        self.onnxruntime_path = './voicevox/python/onnxruntime/lib/libvoicevox_onnxruntime.so.1.17.3'
        self.synthesizer_path = './voicevox/python/dict/open_jtalk_dic_utf_8-1.11'
        self.vvm_folder_path = './voicevox/python/models/vvms'
        
        self.onnxruntime = Onnxruntime.load_once(
            filename=self.onnxruntime_path
        )
        self.synthesizer = Synthesizer(
            self.onnxruntime,
            OpenJtalk(self.synthesizer_path),
            acceleration_mode='AUTO',
            cpu_num_threads=4
        )
        self.voice_style_info = None
        self.audio_query = None
        self.audio_output = None
        
        # Initialize voice options - VoiceVox handles model caching internally
        self.create_voice_style_info()

    def list_styles(self, voice_model_id) -> list[dict[str, any]]:
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
            styles_dict = {
            sub_style_meta.id: sub_style_meta.name 
            for sub_style_meta in style.styles
        }
            style_id_info.append({
                "model_id": voice_model_id,
                "actor_name": voice_actor_name,
                "styles": styles_dict  
            })
        return style_id_info
        
    def fetch_all_available_styles(self) -> list[dict[str, any]]:
        """
        Based on vvm files from /voicevox/python/models/vvms, get all model numbers and their style ids
        Returns organized structure: { actor_name: { style_name: { model_id, style_id } } }
        """
        # Temporary storage for all voice data
        all_voice_data = []
        
        model_id_list = sorted(
            [
                file_name_to_id(filename) 
                for filename in os.listdir(self.vvm_folder_path)
            ]
        )
        
        # First pass: collect all voice data with IDs
        for model_id in model_id_list:
            with VoiceModelFile.open(f'{self.vvm_folder_path}/{model_id}.vvm') as model:
                print(f"Loading voice model number: {model_id}")
                self.synthesizer.load_voice_model(model)
                
                style_metas = self.synthesizer.metas()
                
                for style in style_metas:
                    voice_actor_name = style.name
                    for sub_style_meta in style.styles:
                        all_voice_data.append({
                            "actor_name": voice_actor_name,
                            "style_name": sub_style_meta.name,
                            "style_id": sub_style_meta.id,
                            "model_id": model_id
                        })
        
        # Second pass: organize by actor -> styles with all necessary IDs
        organized_voices = {}
        for voice in all_voice_data:
            actor_name = voice["actor_name"]
            style_name = voice["style_name"]
            
            if actor_name not in organized_voices:
                organized_voices[actor_name] = {}

            # Keep the first occurrence of each style name per actor, 
            # in case same style name appears across multiple models
            if style_name not in organized_voices[actor_name]:
                organized_voices[actor_name][style_name] = {
                    "model_id": voice["model_id"],
                    "style_id": voice["style_id"]
                }
        
        return organized_voices

    def create_voice_style_info(self) -> None:
        """Create JSON optimized for UI dropdown usage"""
        actor_styles_map = self.fetch_all_available_styles()
        
        # Transform to UI-friendly structure
        ui_structure = {
            "actors": list(actor_styles_map.keys()),  # Simple list for first dropdown
            "actor_styles": {
                actor: list(styles.keys())  # Simple list for second dropdown
                for actor, styles in actor_styles_map.items()
            },
            "style_lookup": actor_styles_map  # Complete mapping for backend lookups
        }
        
        # Save to JSON file for debugging purposes
        with open('voice_style_info.json', 'w', encoding='utf-8') as json_file:
            json.dump(ui_structure, json_file, ensure_ascii=False, indent=2)

        # Store the structure for loading model purpose
        self.voice_style_info = ui_structure

    def generate_audio_output_given_voice_ids(self, 
                                              voice_style_id: int, 
                                              text: str):
        """Generate audio output given a specific voice style ID"""
        if len(text) == 0:
            raise ValueError("Text input is empty.")

        self.audio_query = self.synthesizer.create_audio_query(
            text,
            style_id=voice_style_id
        )
        wav = self.synthesizer.synthesis(
            self.audio_query,
            style_id=voice_style_id
        )
        self.audio_output = wav

    def create_wav_file(self) -> None:
        """Create a WAV file from the given audio data"""
        if self.audio_output is not None:
            with open('output.wav', 'wb') as wav_file:
                wav_file.write(self.audio_output)
