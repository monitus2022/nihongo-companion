from pydantic import BaseModel, Field

class LlmRequestBody(BaseModel):
    llm_model_name: str = Field(..., description="The name of the LLM model to use")
    user_prompt: str = Field(..., description="The prompt from the user")
    admin_prompt: str | None = Field(..., description="The prompt from the admin")
    kwargs: dict | None = Field(None, description="Additional keyword arguments")

voicevox_example_character_meta = """
CharacterMeta(name='四国めたん',
        styles=[StyleMeta(name='ノーマル', id=2, type='talk', order=0),
                StyleMeta(name='あまあま', id=0, type='talk', order=1),
                StyleMeta(name='ツンツン', id=6, type='talk', order=2),
                StyleMeta(name='セクシー', id=4, type='talk', order=3)],
        speaker_uuid='7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff',
        version='0.1.0',
        order=0)
"""
