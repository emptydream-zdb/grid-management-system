from sanic.views import HTTPMethodView
from sanic.response import json,HTTPResponse

class device_manage_view(HTTPMethodView):

    async def post(self, request):
        req = request.json

        try:
            result = await request.app.ctx.client.post("<url/path/........>")
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    async def get(self, request):

        try:
            result = await request.app.ctx.client.post("<url/path/........>")
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    async def delete(self, request):
        req = request.json

        try:
            result = await request.app.ctx.client.post("<url/path/........>")
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    async def put(self, request):
        req = request.json

        try:
            result = await request.app.ctx.client.post("<url/path/........>")
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
        