from sanic.views import HTTPMethodView
from sanic.response import json

class event_manage_view(HTTPMethodView):

    async def post(self, request):
        req = request.json
        return json({"message": "User added successfully"})
    
    async def get(self, request):
        req = request.json
        return json({"message": "User added successfully"})
    
    async def delete(self, request):
        req = request.json
        return json({"message": "User added successfully"})
    
    async def put(self, request):
        req = request.json
        return json({"message": "User added successfully"})
    
        