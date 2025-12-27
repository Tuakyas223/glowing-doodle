from fastapi import FastAPI, HTTPException, Response, Depends
from pydantic import BaseModel
import uvicorn
from authx import AuthX, AuthXConfig, TokenPayload

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = "JHSAHIUDASHDWCBNNUIUSI"  # Смени на рандомную хуйню в проде
config.JWT_ACCESS_COOKIE_NAME = "xonsgwbao"
config.JWT_TOKEN_LOCATION = ["cookies"]  # Только куки
config.JWT_ALGORITHM = "HS256"

security = AuthX(config=config)
security.handle_errors(app)  # Обязательно для нормальных ошибок

class UserLoginSchema(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(creds: UserLoginSchema, response: Response):
    if creds.username == "test" and creds.password == "test":
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
    raise HTTPException(status_code=401, detail="Incorrect username or password")

@app.get("/ping")
async def open_ping():
    return {"pong": True, "message": "Anyone can ping me!"}

# Защищённый пинг — самый простой и правильный способ
@app.get("/protected/ping")
async def ping_pong(payload: TokenPayload = security.ACCESS_REQUIRED):
    # payload — dict с 'sub' (uid), 'exp' и т.д.
    uid = payload.sub or "unknown"
    return {"pong": True, "hello": f"user_{uid}"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)