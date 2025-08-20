from pydantic import BaseModel, Field

class LlmRequestBody(BaseModel):
    llm_model_name: str = Field(..., description="The name of the LLM model to use")
    user_prompt: str = Field(..., description="The prompt from the user")
    admin_prompt: str | None = Field(..., description="The prompt from the admin")
    kwargs: dict | None = Field(None, description="Additional keyword arguments")
