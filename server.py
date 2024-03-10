from fastapi import FastAPI
from main import get_reply
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse


class Request(BaseModel):
    messages: list
    model: str = None
    stream: bool = None
    temperature: float = None
    presence_penalty: float = None
    frequency_penalty: float = None
    top_p: int = None
    max_tokens: int = None


app = FastAPI()


@app.post("/v1/chat/completions")
async def answer(request: Request):
    # .model_dump() 相当于 .dict()
    messages = request.model_dump()['messages']
    return EventSourceResponse(get_reply(messages))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6867)