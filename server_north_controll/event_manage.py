import re
from datetime import datetime 
from sanic.views import HTTPMethodView
from sanic.response import json, HTTPResponse
from authorize import authorize

class event_manage_view(HTTPMethodView):

    @authorize("user")
    async def post(self, request):
        req = request.json
        id_room = req.get("id_room")
        id_initiator = req.get("id_initiator")
        if id_room == None or id_initiator == None:
            return json({"errorcode": "2","msg": "id_room and id_initiator is required"}, status=422)
        else:
            if not re.match("^[0-9]+-[0-9]+-[0-9]+$", id_room) and not re.match("^[0-9]+$", id_initiator):
                return json({"errorcode": "2","msg": "id_room or id_initiator is error: id_room must be num-num-num, id_initiator must be num"}, status=422)
        if req.get("event") == None or req.get("event") == "":
            return json({"errorcode": "2","msg": "Don't give empty events!"}, status=422)
        req["time_start"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        req["state"] = "pending"

        try:
            result = await request.app.ctx.client.post("http://localhost:8003/event/v1/",json=req)
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    @authorize("user")
    async def get(self, request, id):
        if not re.match("^[0-9]+-[0-9]+-[0-9]+$", id):
            return json({"errorcode": "0","msg": "id_room is error: must be num-num-num"}, status=422)
        
        #用户只能查看自己的房间
        if request.ctx.group == "user":
            #检测room_id 是否是用户所在的房间
            req_split = id.split("-")
            user_split = request.ctx.id_room.split("-")
            if req_split[:-1] != user_split[:-1]:
                return json({"msg": "You can only check your room!"}, status=401)
        
        num = request.args.get("num")
        state = request.args.get("state")
        try:
            result = await request.app.ctx.client.get("http://localhost:8003/event/v1/{}".format(id),params={"num": num, "state": state})
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    @authorize("user")
    async def delete(self, request, id): # 用户智只能查到自己房间的事件,所以在这里不需要验证
        req = request.json
        try:
            result = await request.app.ctx.client.delete("http://localhost:8003/event/v1/{}".format(id),json=req)
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    @authorize("admin")
    async def put(self, request, id):
        req = request.json
        if req.get("result") == None or req.get("result") == "":
            return json({"errorcode": "2","msg": "Don't give empty result!"}, status=422)
        if req.get("id_processor") == None or req.get("id_processor") == "":
            return json({"errorcode": "2","msg": "id_processor is required!"}, status=422)
        if not re.match("^[0-9]+$", req.get("id_processor")):
            return json({"errorcode": "2","msg": "id_processor is error: must be num"}, status=422)
        req["time_end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        req["state"] = "processed"
        try:
            result = await request.app.ctx.client.put("http://localhost:8003/event/v1/{}".format(id),json=req)
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    