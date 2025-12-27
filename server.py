from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
from authx import AuthX, AuthXConfig

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = "JHSAHIUDASHDWCBNNUIUSI"  # Смени в проде!
config.JWT_ACCESS_COOKIE_NAME = "xonsgwbao"
config.JWT_TOKEN_LOCATION = ["cookies"]  # Только куки
config.JWT_ALGORITHM = "HS256"

security = AuthX(config=config)

# Важно: обработка ошибок authx
security.handle_errors(app)

class UserLoginSchema(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(creds: UserLoginSchema, response=Depends(security.set_access_cookies)):
    if creds.username == "test" and creds.password == "test":
        token = security.create_access_token(uid="12345")
        # authx сам поставит куку через dependency
        return {"message": "Logged in successfully", "user_id": "12345"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

# Открытый пинг (без авторизации)
@app.get("/ping")
async def open_ping():
    return {"pong": True, "message": "Anyone can ping me!"}

# Защищённый пинг
@app.get("/protected/ping")
async def ping_pong(subject: dict = Depends(security.get_current_subject)):
    # subject — это payload токена, например {"uid": "12345", "exp": ..., ...}
    uid = subject.get("uid", "unknown")
    return {"pong": True, "hello": f"user_{uid}"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)