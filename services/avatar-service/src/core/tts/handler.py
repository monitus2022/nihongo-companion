from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
import os
import json
from utils import avatar_service_logger as logger
from config import config


class TextToSpeechHandler:
    def __init__(self) -> None:
        """Initialize TTS handler and optionally load voice options

        Args:
            load_voice_options (bool): Whether to load voice options during init
        """
        # Initialize VoiceVox components
        self.onnxruntime_path = config.tts.get("onnxruntime_path")
        self.synthesizer_path = config.tts.get("synthesizer_path")
        self.vvm_folder_path = config.tts.get("vvm_folder_path")
        self.wav_output_path = config.tts.get("wav_output_path")

        self.onnxruntime = Onnxruntime.load_once(filename=self.onnxruntime_path)
        self.synthesizer = Synthesizer(
            self.onnxruntime,
            OpenJtalk(self.synthesizer_path),
            acceleration_mode=config.tts.get("acceleration_mode"),
            cpu_num_threads=config.tts.get("cpu_num_threads")
        )
        self.voice_style_info = None
        self.audio_query = None
        self.audio_output = None

        # Initialize voice options - VoiceVox handles model caching internally
        self.create_voice_style_info()

    def list_styles(self, voice_model_id) -> list[dict[str, any]]:
        """
        List available styles for the current voice model.
        Refer to schema.py for more details.
        """
        style_metas = self.synthesizer.metas()
        style_id_info = []

        for style in style_metas:
            voice_actor_name = style.name
            styles_dict = {
                sub_style_meta.id: sub_style_meta.name
                for sub_style_meta in style.styles
            }
            style_id_info.append(
                {
                    "model_id": voice_model_id,
                    "actor_name": voice_actor_name,
                    "styles": styles_dict,
                }
            )
        return style_id_info

    def fetch_all_available_styles(self) -> list[dict[str, any]]:
        """
        Based on vvm files from /voicevox/python/models/vvms, get all model numbers and their style ids
        Returns organized structure: { actor_name: { style_name: { model_id, style_id } } }
        """
        # Temporary storage for all voice data
        all_voice_data = []

        model_id_list = sorted(
            [file_name_to_id(filename) for filename in os.listdir(self.vvm_folder_path)]
        )

        # First pass: collect all voice data with IDs
        for model_id in model_id_list:
            with VoiceModelFile.open(f"{self.vvm_folder_path}/{model_id}.vvm") as model:
                self.synthesizer.load_voice_model(model)

                style_metas = self.synthesizer.metas()
                for style in style_metas:
                    voice_actor_name = style.name
                    for sub_style_meta in style.styles:
                        all_voice_data.append(
                            {
                                "actor_name": voice_actor_name,
                                "style_name": sub_style_meta.name,
                                "style_id": sub_style_meta.id,
                                "model_id": model_id,
                            }
                        )
        logger.info(f"✅ Loaded {len(model_id_list)} voice models")

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
                    "style_id": voice["style_id"],
                }
        return organized_voices

    def create_voice_style_info(self) -> None:
        """Create JSON optimized for UI dropdown usage"""
        actor_styles_map = self.fetch_all_available_styles()

        # Transform to UI-friendly structure
        voice_style_info = {
            "actors": list(actor_styles_map.keys()),  # Simple list for first dropdown
            "actor_styles": {
                actor: list(styles.keys())  # Simple list for second dropdown
                for actor, styles in actor_styles_map.items()
            },
            "style_lookup": actor_styles_map,  # Complete mapping for backend lookups
        }

        # Save to JSON file for debugging purposes
        with open("voice_style_info.json", "w", encoding="utf-8") as json_file:
            json.dump(voice_style_info, json_file, ensure_ascii=False, indent=2)

        # Store the structure for loading model purpose
        self.voice_style_info = voice_style_info
        self.style_lookup_info = voice_style_info.get("style_lookup", {})

    def generate_audio_output_given_voice_ids(self, voice_style_id: int, llm_response: str):
        """Generate audio output given a specific voice style ID"""
        if len(llm_response) == 0:
            raise ValueError("Text input is empty.")

        self.audio_query = self.synthesizer.create_audio_query(
            text=llm_response, 
            style_id=voice_style_id
        )
        wav = self.synthesizer.synthesis(self.audio_query, style_id=voice_style_id)
        self.audio_output = wav

    def get_voice_id_from_names(self, voice_actor_name: str, voice_style_name: str) -> tuple[int, int]:
        """
        Get style_id from voice actor and style names.
        """
        if voice_actor_name not in self.style_lookup_info:
            available_actors = list(self.style_lookup_info.keys())
            raise ValueError(f"Voice actor '{voice_actor_name}' not found. Available: {available_actors}")

        actor_styles = self.style_lookup_info[voice_actor_name]
        if voice_style_name not in actor_styles:
            available_styles = list(actor_styles.keys())
            raise ValueError(f"Style '{voice_style_name}' not found for actor '{voice_actor_name}'. Available: {available_styles}")
        
        style_info = actor_styles[voice_style_name]
        return style_info["style_id"]

    def create_wav_from_llm_response(
        self,
        llm_response: str,
        voice_actor_name: str,
        voice_style_name: str,
    ) -> None:
        """
        Create a WAV file from the given llm response using the specified voice actor and style.
        """
        # Find style id based on names
        style_id = self.get_voice_id_from_names(
            voice_actor_name, voice_style_name)
        if style_id is None:
            return None

        # Generate audio output
        logger.debug(f"Generating audio for text: {llm_response} with actor: {voice_actor_name}, style: {voice_style_name}")
        self.generate_audio_output_given_voice_ids(
            voice_style_id=style_id, 
            llm_response=llm_response
            )

        # Output as wav for UI purpose for debugging
        create_wav_file(
            audio_output=self.audio_output, 
            wav_output_path=self.wav_output_path
            )
        logger.info(f"Created WAV file at: {self.wav_output_path}")

def file_name_to_id(filename: str) -> int:
    """Extract the model ID from the filename."""
    return int(filename.split('.')[0])

def create_wav_file(audio_output, wav_output_path) -> None:
    """Create a WAV file from the given audio data"""
    with open(wav_output_path, "wb") as wav_file:
        wav_file.write(audio_output)
        