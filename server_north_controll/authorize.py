import jwt,time
import datetime
from sanic.response import json, HTTPResponse
from enum import IntEnum
from functools import wraps


class role(IntEnum):
    """
    用户权限组别
    """
    UNKNOWN = 1
    USER = 2
    NONE = 3


from functools import wraps
from inspect import signature

def authorize(required_group: str):
    """
    装饰器方法:
    :param required_group: 需要的最小权限组别
    """
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            # 检查函数的第一个参数是否是 'self'
            sig = signature(f)
            parameters = sig.parameters
            is_method = list(parameters.keys())[0] == 'self'

            # 如果是类方法，第一个参数是 'self'
            # 如果是函数，第一个参数是 'request'
            if is_method:
                request = args[1]
            else:
                request = args[0]
                
            req_group = role[required_group.upper()]
            token = request.headers.get('Authorization')
            if not token:
                if required_group != "none":
                    return json({"msg":"No token provided!"},status=401)
                group = role.NONE
            else:    
                try:
                    # 验证JWT并获取用户角色
                    data = jwt.decode(token, request.app.config.SECRET_KEY, algorithms=['HS256'])
                    group = role[data['group'].upper()]
                except jwt.ExpiredSignatureError:
                    return json({"msg":"Token expired!"},status=401)
                except jwt.InvalidTokenError:
                    return json({"msg":"Token invalid!"},status=401)
            # 检查用户是否有足够的权限
            if group < req_group:
                return json({"msg":"Insufficient permissions!"},status=401)
            
            #把Token中有用字段放入request.ctx中
            if group != role.NONE:
                request.ctx.group = data['group']
                request.ctx.id_user = data['id_user']
                request.ctx.id_room = data['id_room']
            else:
                request.ctx.group = "none"
            return await f(request, *args[1:], **kwargs)

        return decorated_function
    return decorator


async def login(request):
    """
    用户登录
    """
    # 验证用户凭据并获取用户角色
    # 这里只是一个示例，你需要根据你的数据库来实现
    id_user = request.json.get('id_user')
    password = request.json.get('password')
    # 验证密码并获取用户组别以及所属房间床位id
    result, data = await _vali_password(request, id_user, password)
    if not result:
        return data
    # 创建JWT
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    exp = now + datetime.timedelta(hours=2)
    refresh_exp = now + datetime.timedelta(days=7)
    token = jwt.encode(payload={'id_user':id_user,'group': data[0], 'id_room':data[1], 'exp': exp}, key=request.app.config.SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(payload={'id_user': id_user,'group': data[0], 'id_room':data[1], 'exp': refresh_exp}, key=request.app.config.SECRET_KEY_REFRESH, algorithm='HS256')
    return json({'msg':'logging successful!','data':{'token': token, 'token_refresh': refresh_token}})

async def refresh(request):
    """
    刷新Token
    """
    token = request.headers.get('Authorization')
    if not token:
        return json({"msg":"No token provided!"},status=401)
    try:
        data = jwt.decode(token, request.app.config.SECRET_KEY_REFRESH, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return json({"msg":"Token expired!"},status=401)
    except jwt.InvalidTokenError:
        return json({"msg":"Token invalid!"},status=401)

    # 创建JWT
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    exp = now + datetime.timedelta(hours=2)
    refresh_exp = now + datetime.timedelta(days=7)
    token = jwt.encode(payload={'id_user':data['id_user'],'group': data["group"], 'id_room':data["id_room"], 'exp': exp,}, key=request.app.config.SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(payload={'id_user': data['id_user'],'group': data["group"], 'id_room':data["id_room"], 'exp': refresh_exp}, key=request.app.config.SECRET_KEY_REFRESH, algorithm='HS256')
    return json({'msg':'refresh successful!','data':{'token': token, 'token_refresh': refresh_token}})

async def _vali_password(request, id_user, password):
    result = await request.app.ctx.client.get("http://localhost:8001/user/v1/{}".format(id_user), params={"class": "user", "passwd": "true"})
    if result.status_code != 201:
        return False, HTTPResponse(body=result.content, status=result.status_code)
    data = result.json()
    if password != data['password']:
        return False, json({'msg': 'Invalid credentials'}, status=401)
    return True, (data['group'],data['id_room'])