from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
import authx
from authx import AuthX, AuthXConfig

app = FastAPI()

# Конфиг authx
config = AuthXConfig()
config.JWT_SECRET_KEY = "JHSAHIUDASHDWCBNNUIUSI"  # В продакшене смени на что-то серьёзное и из env!
config.JWT_ACCESS_COOKIE_NAME = "xonsgwbao"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_ALGORITHM = "HS256"  # по умолчанию и так, но на всякий

security = AuthX(config=config)

class UserLoginSchema(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(creds: UserLoginSchema, response=Depends(security.set_access_cookies)):
    if creds.username == "test" and creds.password == "test":
        token = security.create_access_token(uid="12345")
        # authx сам установит куку через response
        response.set_cookie(
            key=config.JWT_ACCESS_COOKIE_NAME,
            value=token,
            httponly=True,
            max_age=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return {"message": "Logged in successfully", "user_id": "12345"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

# Защищённый эндпоинт — только с валидной кукой
@app.get("/protected/ping")
async def ping_pong(user=Depends(security.get_current_user)):
    # user будет dict с данными из токена, например user["uid"]
    return {"pong": True, "hello": f"user_{user.get('uid', 'unknown')}"}

# Для теста — открытый пинг без авторизации
@app.get("/ping")
async def open_ping():
    return {"pong": True, "message": "Anyone can ping me!"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)