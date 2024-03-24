from sanic import Sanic
from sanic.response import json
from sanic import Request

app = Sanic("user_manager")

@app.post('/user/v1', name= "add_user")
async def add_user(request: Request):
    req = request.json
    return json({"message": "User added successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)