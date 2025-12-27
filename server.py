import fastapi
import uvicorn

app = fastapi.FastAPI()

@app.get("/users", tags=["users"], summary=["getusers"])
async def get_users():
    return [{"id": 1, "name": "Artem"}]

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)