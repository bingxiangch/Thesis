from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse
from typing import Literal
from private_gpt.schemas.context_filter import ContextFilter
from private_gpt.server.chat.chat_service import ChatService
from private_gpt.server.utils.auth import authenticated

chat_router = APIRouter(prefix="/v1", dependencies=[Depends(authenticated)])

class Message(BaseModel):
    """Inference result, with the source of the message.

    Role could be the assistant or system
    (providing a default response, not AI generated).
    """

    role: Literal["assistant", "system", "user"] = Field(default="user")
    content: str | None

class CompletionsBody(BaseModel):
    prompt: str
    system_prompt: str | None = None
    use_context: bool = False
    context_filter: ContextFilter | None = None
    include_sources: bool = True
    stream: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "prompt",
                    "include_sources": False,
                }
            ]
        }
    }


@chat_router.post(
    "/chat",
    response_model=None,
    summary="chat",
    tags=["chat"],
)
def prompt_completion(
    request: Request, body: CompletionsBody
):
    """

    Given a prompt, the model will return one predicted completion.

    When using `'include_sources': true`, the API will return the source Chunks used
    to create the response, which come from the context provided.
    ```
    """
    messages = [Message(content=body.prompt, role="user")]
    # If system prompt is passed, create a fake message with the system prompt.
    if body.system_prompt:
        messages.insert(0, Message(content=body.system_prompt, role="system"))
    service = request.state.injector.get(ChatService)
    completion = service.chat(
        messages=messages,
        use_context=True,
        context_filter=None,
    )

    return {
        "response": completion.response,
        "sources": completion.sources if body.include_sources else None
    }

