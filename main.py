import re
from typing import Callable
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from src.routes import users, auth, photo, comments

app = FastAPI()


origins = [
    "http://localhost:8000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_agent_ban_list = [r"Googlebot", r"Python-urllib"]

@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    """
    Middleware to ban specific User-Agent strings.

    Args:
        request (Request): The incoming FastAPI request.
        call_next (Callable): The next callable in the middleware stack.

    Returns:
        JSONResponse: If the User-Agent matches any of the patterns in the ban list,
            returns a JSONResponse with a 403 FORBIDDEN status.
        Response: Calls the next middleware or route in the stack.
    """
    print(request.headers.get("Authorization"))
    user_agent = request.headers.get("user-agent")
    print(user_agent)
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
    response = await call_next(request)
    return response


BASE_DIR = Path("../..")


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(photo.router, prefix="/api")
app.include_router(comments.router, prefix="/api")

templates = Jinja2Templates(directory=BASE_DIR / "src" / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    Endpoint to serve the main HTML page.

    Args:
        request (Request): The incoming FastAPI request.

    Returns:
        TemplateResponse: Returns the rendered HTML template response.
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "our": "Build group WebPython #16"}
    )
