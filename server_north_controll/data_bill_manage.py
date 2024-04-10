from sanic.views import HTTPMethodView
from sanic.response import json, HTTPResponse
from authorize import authorize
import re

class elecbill_manage_view(HTTPMethodView):
    """
    电费管理
    """
    @authorize("user")
    async def get(self, request, room_id):
        if not re.match(r"^[0-9]+-[0-9]+-[0-9]+$", room_id):
            return json({"errorcode": "0", "msg": "room_id error, must be num-num-num"}, status=422)
        
        #用户只能查看自己的房间
        if request.ctx.group == "user":
            #检测room_id 是否是用户所在的房间
            req_split = room_id.split("-")
            user_split = request.ctx.id_room.split("-")
            if req_split[:-1] != user_split[:-1]:
                return json({"msg": "You can only check your room!"}, status=401)

        try:
            result = await request.app.ctx.client.get("http://localhost:8010/elecbill/v1/{}".format(room_id))
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    @authorize("admin")
    async def delete(self, request, room_id):
        if not re.match(r"^[0-9]+-[0-9]+-[0-9]+$", room_id):
            return json({"errorcode": "0", "msg": "room_id error, must be num-num-num"}, status=422)
        try:
            result = await request.app.ctx.client.delete("http://localhost:8010/elecbill/v1/{}".format(room_id))
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    @authorize("user")
    async def put(self, request, room_id):
        if not re.match(r"^[0-9]+-[0-9]+-[0-9]+$", room_id):
            return json({"errorcode": "0", "msg": "room_id error, must be num-num-num"}, status=422)
        req = request.json
        if not isinstance(req["num"], float):
            return json({"errorcode": "2", "msg": "num error, must be float"}, status=422)
        
        #用户只能充值
        if request.ctx.group == "user":
            if req["num"] <= 0:
                return json({"msg": "You can only recharge!"}, status=401)
        
        req["id"] = room_id
        try:
            result = await request.app.ctx.client.put("http://localhost:8010/elecbill/v1", json=req)
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
@authorize("user")
async def get_elec_used_data(request, room_id):
    """
    获取某个房间的用电数据
    """
    if not re.match(r"^[0-9]+-[0-9]+-[0-9]+$", room_id):
        return json({"errorcode": "0", "msg": "room_id error, must be num-num-num"}, status=422)
    
    #用户只能查看自己的房间
    if request.ctx.group == "user":
        #检测room_id 是否是用户所在的房间
        req_split = room_id.split("-")
        user_split = request.ctx.id_room.split("-")
        if req_split[:-1] != user_split[:-1]:
            return json({"msg": "You can only check your room!"}, status=401)
    
    time_start = request.args.get("time_start")
    time_end = request.args.get("time_end")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", time_start) or not re.match(r"^\d{4}-\d{2}-\d{2}$", time_end):
        return json({"errorcode": "2", "msg": "time error, must be yyyy-mm-dd"}, status=422)
    try:
        result = await request.app.ctx.client.get("http://localhost:8010/data/v1/{}".format(room_id), params={"time_start": time_start, "time_end": time_end})
    except Exception as e:
        return json({"msg": "error: {}".format(str(e))}, status=400)
    return HTTPResponse(body=result.content, status=result.status_code)

@authorize("user")
async def get_elec_real_data(request, room_id):
    """
    获取某个房间的实时用电数据
    """
    if not re.match(r"^[0-9]+-[0-9]+-[0-9]+$", room_id):
        return json({"errorcode": "0", "msg": "room_id error, must be num-num-num"}, status=422)
    
    if request.ctx.group == "user":
        #检测room_id 是否是用户所在的房间
        req_split = room_id.split("-")
        user_split = request.ctx.id_room.split("-")
        if req_split[:-1] != user_split[:-1]:
            return json({"msg": "You can only check your room!"}, status=401)
    
    try:
        result = await request.app.ctx.client.get("http://localhost:8002/data/v1/{}".format(room_id))
    except Exception as e:
        return json({"msg": "error: {}".format(str(e))}, status=400)
    return HTTPResponse(body=result.content, status=result.status_code)