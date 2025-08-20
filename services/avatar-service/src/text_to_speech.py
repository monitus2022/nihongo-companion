from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
import os
import json
from utils import file_name_to_id


class TextToSpeechHandler:
    def __init__(self) -> None:
        """Initialize TTS handler and optionally load voice options

        Args:
            load_voice_options (bool): Whether to load voice options during init
        """
        # Initialize VoiceVox components
        self.onnxruntime_path = (
            "./voicevox/python/onnxruntime/lib/libvoicevox_onnxruntime.so.1.17.3"
        )
        self.synthesizer_path = "./voicevox/python/dict/open_jtalk_dic_utf_8-1.11"
        self.vvm_folder_path = "./voicevox/python/models/vvms"
        self.wav_output_path = "output.wav"

        self.onnxruntime = Onnxruntime.load_once(filename=self.onnxruntime_path)
        self.synthesizer = Synthesizer(
            self.onnxruntime,
            OpenJtalk(self.synthesizer_path),
            acceleration_mode="AUTO",
            cpu_num_threads=4,
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
        print(f"Begin loading voice models...")
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
        print(f"✅ Loaded {len(model_id_list)} models")

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

    def create_wav_file(self) -> None:
        """Create a WAV file from the given audio data"""
        if self.audio_output is not None:
            with open(self.wav_output_path, "wb") as wav_file:
                wav_file.write(self.audio_output)

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
        print(f"Generating audio for text: {llm_response} with actor: {voice_actor_name}, style: {voice_style_name}")
        self.generate_audio_output_given_voice_ids(
            voice_style_id=style_id, 
            llm_response=llm_response
            )

        # Output as wav for UI purpose for debugging
        self.create_wav_file()
        print(f"Created WAV file at: {self.wav_output_path}")