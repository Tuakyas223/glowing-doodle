from fastapi import FastAPI, HTTPException, Response, Depends
from pydantic import BaseModel
import uvicorn
from authx import AuthX, AuthXConfig, TokenPayload

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = "JHSAHIUDASHDWCBNNUIUSI"  # Смени на сильный ключ!
config.JWT_ACCESS_COOKIE_NAME = "xonsgwbao"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_ALGORITHM = "HS256"

security = AuthX(config=config)
security.handle_errors(app)

# "БД" в памяти для HWID юзера "test" (в реале — файл или настоящая БД)
registered_hwid: str | None = None

class LoginSchema(BaseModel):
    username: str
    password: str
    hwid: str

@app.post("/login")
async def login(creds: LoginSchema, response: Response):
    global registered_hwid
    if creds.username != "test" or creds.password != "test":
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # Проверка/регистрация HWID
    if registered_hwid is None:
        registered_hwid = creds.hwid
        print(f"[SERVER] Новый HWID зарегистрирован: {registered_hwid}")
    elif registered_hwid != creds.hwid:
        raise HTTPException(status_code=403, detail="HWID mismatch! Аккаунт привязан к другому ПК.")

    token = security.create_access_token(uid="12345")
    response.set_cookie(
        key=config.JWT_ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # True на HTTPS
        max_age=3600 * 24,
    )
    return {"message": "Logged in successfully", "user_id": "12345"}

@app.get("/ping")
async def open_ping():
    return {"pong": True, "message": "Anyone can ping me!"}

@app.get("/protected/ping")
async def ping_pong(payload: TokenPayload = security.ACCESS_REQUIRED):
    uid = payload.sub or "unknown"
    return {"pong": True, "hello": f"user_{uid}"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)