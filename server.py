from fastapi import FastAPI, HTTPException, Depends, Response
from pydantic import BaseModel
import uvicorn
from authx import AuthX, AuthXConfig, RequestToken

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = "JHSAHIUDASHDWCBNNUIUSI"  # Смени нахуй в проде
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
        # Вручную ставим HttpOnly куку
        response.set_cookie(
            key=config.JWT_ACCESS_COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="lax",  # или "strict"/"none" если нужно
            secure=False,    # True в проде с HTTPS
            max_age=3600 * 24  # Например, день
        )
        return {"message": "Logged in successfully", "user_id": "12345"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

# Открытый пинг
@app.get("/ping")
async def open_ping():
    return {"pong": True, "message": "Anyone can ping me!"}

# Защищённый пинг
@app.get("/protected/ping")
async def ping_pong(token: RequestToken = Depends(security.get_token_from_request)):
    # Здесь верифицируем токен и получаем subject (payload)
    try:
        payload = security.verify_token(token=token)
        uid = payload.get("uid", "unknown")
        return {"pong": True, "hello": f"user_{uid}"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)