from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status, Security
from .auth import verify_password, create_access_token, decode_access_token, get_password_hash
from private_gpt.models.models import User, SessionLocal    
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse
from typing import Literal
from private_gpt.schemas.context_filter import ContextFilter
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from private_gpt.models.models import File, FileDoc
# from private_gpt.server.chat.chat_service import ChatService
from private_gpt.services.chat_service import ChatService
from private_gpt.server.utils.auth import authenticated
from private_gpt.db.session import get_db
from private_gpt.services.chunks_service import Chunk, ChunksService

chat_router = APIRouter(prefix="/v1", dependencies=[Depends(authenticated)])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)

    if token_data is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.get("sub")).first()
    if user is None:
        raise credentials_exception

    return user

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

def get_docs_for_user(user: User, db: Session):
    # Get all FileDoc entries where the access level of the associated File
    # is less than or equal to the user's access level
    file_docs = db.query(FileDoc).\
        join(File, File.id == FileDoc.file_id).\
        filter(File.access_level == user.access_level).\
        all()

    # Extract doc_ids from the query result
    doc_ids = [file_doc.doc_id for file_doc in file_docs]
    return doc_ids


def get_file_access_level_by_doc_id(doc_id: str, db: Session):
    # Join FileDoc and File tables and filter by doc_id
    result = db.query(File).\
        join(FileDoc, File.id == FileDoc.file_id).\
        filter(FileDoc.doc_id == doc_id).\
        first()

    if result:
        return result.access_level
    else:
        return None  # or you can raise an exception if appropriate


@chat_router.post(
    "/chat",
    response_model=None,
    summary="chat",
    tags=["chat"],
)
def prompt_completion(
    request: Request, body: CompletionsBody, current_user: User = Security(get_current_user), db: Session = Depends(get_db)
):
    """
    , current_user: User = Security(get_current_user)
    Given a prompt, the model will return one predicted completion.

    When using `'include_sources': true`, the API will return the source Chunks used
    to create the response, which come from the context provided.
    ```
    """
    breakpoint()
    docs_filter = ContextFilter(docs_ids = get_docs_for_user(current_user, db))


    chunks_service = request.state.injector.get(ChunksService)
    most_relevant_chunk = chunks_service.retrieve_most_relevant(
        body.prompt
    )
    most_relevant_doc_id = most_relevant_chunk.document.doc_id
    access_level = None
    if most_relevant_chunk.score > 0.5 and most_relevant_doc_id not in get_docs_for_user(current_user, db):
        #you can ask some one for help. 

        access_level =  get_file_access_level_by_doc_id(most_relevant_doc_id, db)
    messages = [Message(content=body.prompt, role="user")]
    # If system prompt is passed, create a fake message with the system prompt.
    if body.system_prompt:
        messages.insert(0, Message(content=body.system_prompt, role="system"))
    else:
        messages.insert(0, Message(content="You can only answer questions about the provided context. If you know the answer but it is not based in the provided context, don't provide the answer, just response the answer is not in the knowledge base or you don't have related permissions to access.", role="system"))
        
    service = request.state.injector.get(ChatService)
    

    completion = service.chat(
        messages=messages,
        use_context=True,
        context_filter=docs_filter,
    )
    if access_level:
        completion.response = completion.response + " You can contact users with access level " + str(access_level) + " for help or get more accurate answer"

    return {
        "response": completion.response,
        "sources": completion.sources if body.include_sources else None
    }

