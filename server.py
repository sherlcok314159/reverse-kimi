from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from main import get_reply
from utils import load_config

app = FastAPI()
TOKEN = load_config()['token']
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class Request(BaseModel):
    messages: list
    model: str = None
    stream: bool = None
    temperature: float = None
    presence_penalty: float = None
    frequency_penalty: float = None
    top_p: int = None
    max_tokens: int = None


@app.post("/v1/chat/completions")
async def answer(request: Request, token: str = Depends(oauth2_scheme)):
    if token != TOKEN:
        print(f"请求的 token: {token}")
        print(f"设置的 token: {TOKEN}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # .model_dump() 相当于 .dict()
    messages = request.model_dump()['messages']
    return EventSourceResponse(get_reply(messages))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6867)
