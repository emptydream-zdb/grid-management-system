from sanic.views import HTTPMethodView
from sanic.response import json,HTTPResponse
from authorize import authorize
from data_models import Device_post, Device_put
from pydantic import ValidationError
import re

class device_manage_view(HTTPMethodView):

    @authorize("none")
    async def post(self, request, id):
        if re.match(r"^[0-9]+-[0-9]+-[0-9]+$", id) is None:
            return json({"errorcode": "0", "msg": "Path error: \"id\" device is required and must be a num-num-num"}, status=422)
        req = request.json
        try:
            Device_post(**req)
        except ValidationError as e:
            return json({"errorcode": "2", "msg": "The device data error: {}".format(str(e))}, status=422)
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        
        try:
            result = await request.app.ctx.client.post("http://localhost:8011/device/v1/{}".format(id), json=req)
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
        
    
    @authorize("none")
    async def get(self, request, id):
        if re.match(r"^[0-9]+-[0-9]+-[0-9]+$", id) is None:
            return json({"errorcode": "0", "msg": "Path error: \"id\" device is required and must be a num-num-num"}, status=422)
        state = request.args.get("state")
        if state is not None:
            if state not in ["normal", "lost"]:
                return json({"errorcode": "1", "msg": "Query error: \"state\" arg must be \"normal\" or \"lost\""}, status=422)
        try:
            result = await request.app.ctx.client.get("http://localhost:8011/device/v1", params={"id": id, "state": state})
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    @authorize("none")
    async def delete(self, request, id):
        if re.match(r"^[0-9]+-[0-9]+-[0-9]+$", id) is None:
            return json({"errorcode": "0", "msg": "Path error: \"id\" device is required and must be a num-num-num"}, status=422)
        try:
            result = await request.app.ctx.client.delete("http://localhost:8011/device/v1/{}".format(id))
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    @authorize("none")
    async def put(self, request, id):
        if re.match(r"^[0-9]+-[0-9]+-[0-9]+$", id) is None:
            return json({"errorcode": "0", "msg": "Path error: \"id\" device is required and must be a num-num-num"}, status=422)
        req = request.json
        try:
            Device_put(**req)
        except ValidationError as e:
            return json({"errorcode": "2", "msg": "The device data error: {}".format(str(e))}, status=422)
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        try:
            result = await request.app.ctx.client.put("http://localhost:8011/device/v1/{}".format(id), json=req)
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
        