import re
from sanic.views import HTTPMethodView
from sanic.response import json, HTTPResponse
from sanic_ext import validate
from pydantic import BaseModel, Field # 使用pydantic用来做参数校验
from pydantic import ValidationError # 引入ValidationError异常类

# 以下为Body参数数据模型定义, 建议在每个HTTPMethodView同文件中定义一个数据模型, 用于数据校验
class User_Post(BaseModel): # 新建用户 User Model
    # Field 用来定制数据约束, 第一个参数为默认值, ... 表示必填, pattern 为正则表达式约束, max_length 为最大长度约束
    id_user: str = Field(...) 
    id_room: str = Field(..., pattern = "^[0-9]+-[0-9]+-[0-9]+$",max_length = 20)
    name: str = Field(..., max_length = 20)
    group: str = Field(..., pattern="^(admin|user)$")
    work_unit: str = Field(..., max_length = 255)

class User_Put(BaseModel): # 更新用户 User Model
    # Field 用来定制数据约束, 第一个参数为默认值, ... 表示必填, pattern 为正则表达式约束, max_length 为最大长度约束
    id_user: str = Field(None) 
    id_room: str = Field(None, pattern = "^[0-9]+-[0-9]+-[0-9]+$",max_length = 20)
    password: str = Field(None, max_length = 255)
    name: str = Field(None, max_length = 20)
    group: str = Field(None, pattern="^(admin|user)$")
    work_unit: str = Field(None, max_length = 255)


class user_manage_view(HTTPMethodView):
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
    
    async def get(self, request, id):
        """
        查询用户, 参数校验, 转发请求
        """
        req = request.json
        cls = request.args.get("class")
        cls_pattern = r"^(room|user)$"
        cls = "" if cls == None else cls
        if not re.match(cls_pattern, cls):
            return json({"errorcode": "1", "msg": "Query error: \"class\" arg is required and must be \"user\" or \"room\""}, status=422)
        if cls == "user":
            user_pattern = r"^[0-9]+$"
            if not re.match(user_pattern, id):
                return json({"errorcode": "0", "msg": "Path error: \"id\" user is required and must be a number"}, status=422)
        else:
            room_pattern = r"^[0-9]+-[0-9]+-[0-9]+$"
            if not re.match(room_pattern, id):
                return json({"errorcode": "0", "msg": "Path error: \"id\" room is required and must be a number-number-number"}, status=422)
        try:
            result = await request.app.ctx.client.get("http://localhost:8001/user/v1/{}".format(id), params={"class": cls})
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    async def delete(self, request, id):
        user_pattern = r"^[0-9]+$"
        if not re.match(user_pattern, id):
            return json({"errorcode": "0", "msg": "Path error: \"id\" is required and must be a number"}, status=422)
        try:
            result = await request.app.ctx.client.delete("http://localhost:8001/user/v1/{}".format(id))
        except Exception as e:
            return json({"msg": "error: {}".format(str(e))}, status=400)
        return HTTPResponse(body=result.content, status=result.status_code)
    
    async def put(self, request):
        req = request.json
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
    