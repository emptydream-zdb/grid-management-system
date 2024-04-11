import re
from sanic.views import HTTPMethodView
from sanic.response import json, HTTPResponse
from sanic_ext import validate
from data_models import User_Post, User_Put
from pydantic import ValidationError # 引入ValidationError异常类
from authorize import authorize



class user_manage_view(HTTPMethodView):
    @authorize("admin")
    async def post(self, request):
        """
        添加用户, 参数校验, 转发请求
        """
        req = request.json
        for i, item in enumerate(req):
            try:
                User_Post(**item)
            except ValidationError as e:
                return json({"errorcode": "2", "msg": "The NO.{} user data error: {}".format(i, str(e))}, status=422)
            except Exception as e:
                return json({"msg": "error: {}".format(str(e))}, status=400)
            item["password"] = item["id_user"][-6:]
        try:
            result = await request.app.ctx.client.post("http://localhost:8001/user/v1",json=req)
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    @authorize("user")
    async def get(self, request, id):
        """
        查询用户, 参数校验, 转发请求
        """
        cls = request.args.get("class")
        cls_pattern = r"^(room|user)$"
        cls = "" if cls == None else cls
        if not re.match(cls_pattern, cls):
            return json({"errorcode": "1", "msg": "Query error: \"class\" arg is required and must be \"user\" or \"room\""}, status=422)
        if cls == "user":
            user_pattern = r"^[0-9]+$"
            if not re.match(user_pattern, id):
                return json({"errorcode": "0", "msg": "Path error: \"id\" user is required and must be a number"}, status=422)
            
            # 用户只能查看自己的信息
            if request.ctx.group == "user":
                if id != request.ctx.id_user:
                    return json({"msg": "You can only check your info!"}, status=401)
        else:
            # 用户只能查看自己的信息
            if request.ctx.group == "user":
            #检测room_id 是否是用户所在的房间
                req_split = id.split("-")
                user_split = request.ctx.id_room.split("-")
                if req_split[:-1] != user_split[:-1]:
                    return json({"msg": "You can only check your room!"}, status=401)
            
            room_pattern = r"^[0-9]+-[0-9]+-[0-9]+$"
            if not re.match(room_pattern, id):
                return json({"errorcode": "0", "msg": "Path error: \"id\" room is required and must be a number-number-number"}, status=422)
        try:
            result = await request.app.ctx.client.get("http://localhost:8001/user/v1/{}".format(id), params={"class": cls})
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    @authorize("admin")
    async def delete(self, request, id):
        user_pattern = r"^[0-9]+$"
        if not re.match(user_pattern, id):
            return json({"errorcode": "0", "msg": "Path error: \"id\" is required and must be a number"}, status=422)
        try:
            result = await request.app.ctx.client.delete("http://localhost:8001/user/v1/{}".format(id))
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    @authorize("user")
    async def put(self, request):
        req = request.json
        group = request.ctx.user_group
        if group == "user":
            if len(req) > 1 or req[0].get("id_user") != request.ctx.id_user:
                return json({"msg": "Insufficient permissions!"}, status=401)
        for i, item in enumerate(req):
            try:
                User_Put(**item)
            except ValidationError as e:
                return json({"errorcode": "2", "msg": "The NO.{} user data error: {}".format(i, str(e))}, status=422)
            except Exception as e:
                return json({"msg": "error: {}".format(str(e))}, status=400)
        try:
            result = await request.app.ctx.client.put("http://localhost:8001/user/v1/".format(id), json=req)
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    