from typing import Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from private_gpt.schemas.context_filter import ContextFilter
from private_gpt.server.chunks.chunks_service import Chunk, ChunksService
from private_gpt.server.utils.auth import authenticated

chunks_router = APIRouter(prefix="/v1", dependencies=[Depends(authenticated)])


class ChunksBody(BaseModel):
    text: str = Field(examples=["prompt"])



class ChunksResponse(BaseModel):
    object: Literal["list"]
    model: Literal["authr-RAG"]
    data: list[Chunk]


@chunks_router.post("/chunks", tags=["Context Chunks"])
def chunks_retrieval(request: Request, body: ChunksBody) -> ChunksResponse:
    """Given a `text`, returns the all relevant chunks from the ingested documents.
    """
    service = request.state.injector.get(ChunksService)
    results = service.retrieve_relevant(
        body.text, None, 10, 2
    )
    return ChunksResponse(
        object="list",
        model="authr-RAG",
        data=results,
    )

@chunks_router.post("/most_relevant_chunk", tags=["Context Chunks"])
def most_relevant_chunk(request: Request, body: ChunksBody):
    """Given a `text`, returns the most relevant chunks from the ingested documents.
    """
    service = request.state.injector.get(ChunksService)
    results = service.retrieve_most_relevant(
        body.text
    )
    return results