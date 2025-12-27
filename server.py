from fastapi import FastAPI, HTTPException, Response, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from authx import AuthX, AuthXConfig, TokenPayload
import uvicorn
import bcrypt
import platform
import uuid
from typing import Optional

# ---------------- CONFIG ----------------
app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="CHANGE_THIS_SECRET_KEY_123456",
    JWT_ACCESS_COOKIE_NAME="auth_token",
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_ALGORITHM="HS256",
)

security = AuthX(config=config)
security.handle_errors(app)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- "DATABASE" ----------------
# username -> {password_hash, hwid}
users_db: dict[str, dict] = {}

# ---------------- HELPERS ----------------
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

def generate_hwid() -> str:
    """
    Генерируем HWID на основе machine uuid + platform
    """
    raw = str(uuid.getnode()) + platform.node() + platform.system() + platform.version()
    import hashlib, base64
    sha = hashlib.sha256(raw.encode()).digest()
    return base64.b64encode(sha).decode()

# ---------------- OPTIONAL AUTH ----------------
async def optional_auth(request: Request) -> Optional[TokenPayload]:
    try:
        token = await security.get_token_from_request(request, locations=None)
        return security.verify_token(token.raw, verify_type=True)
    except Exception:
        return None

# ---------------- AUTH / API ----------------
@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    response: Response = None
):
    if username in users_db:
        # Уже зарегистрирован → редирект на dashboard
        return RedirectResponse("/dashboard", status_code=303)

    users_db[username] = {
        "password": hash_password(password),
        "hwid": None  # HWID будет сгенерирован при первом логине
    }

    # JWT cookie
    token = security.create_access_token(uid=username)
    resp = RedirectResponse("/dashboard", status_code=303)
    resp.set_cookie(
        key=config.JWT_ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=86400,
    )
    return resp

@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    response: Response = None
):
    user = users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(401, "Invalid credentials")

    # Генерация HWID при первом логине
    if user["hwid"] is None:
        user["hwid"] = generate_hwid()

    token = security.create_access_token(uid=username)
    resp = RedirectResponse("/dashboard", status_code=303)
    resp.set_cookie(
        key=config.JWT_ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=86400,
    )
    return resp

@app.post("/logout")
async def logout(response: Response):
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return response

@app.get("/me")
async def me(payload: TokenPayload = security.ACCESS_REQUIRED):
    username = payload.sub
    user = users_db.get(username)
    if not user:
        raise HTTPException(404)
    return {"username": username, "hwid": user["hwid"]}

# ---------------- WEB ----------------
@app.get("/")
async def login_page(request: Request, payload: Optional[TokenPayload] = Depends(optional_auth)):
    if payload:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register_page")
async def register_page(request: Request, payload: Optional[TokenPayload] = Depends(optional_auth)):
    if payload:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request, payload: TokenPayload = security.ACCESS_REQUIRED):
    user = users_db.get(payload.sub)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "username": payload.sub, "hwid": user["hwid"]}
    )

# ---------------- PROTECTED TEST ----------------
@app.get("/protected/ping")
async def protected_ping(payload: TokenPayload = security.ACCESS_REQUIRED):
    return {"pong": True, "user": payload.sub, "hwid": users_db[payload.sub]["hwid"]}

# ---------------- RUN ----------------
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=1242, reload=True)
