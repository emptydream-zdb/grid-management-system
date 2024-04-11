import sys, os
current_file_dir = os.path.dirname(__file__) # 获取当前文件的父目录
parent_dir = os.path.join(current_file_dir, "../") # 获取父目录
sys.path.append(parent_dir) # 添加父级目录到系统路径,以解决模块导入问题


from sanic import Sanic
from sanic import response
import aioredis
import ujson as js

port_run = 8002 # your port number
dev = False

app = Sanic("realtime_data")

@app.listener('before_server_start')
async def start_redis(appp) -> None:
    """
    Set up the database connection before the server starts.
    add the database connection to the app context so that we can access it in HTTPMethodView.
    
    Args:
        app: The Sanic application object.
    """
    app.ctx.redis = await aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)

@app.listener('after_server_stop')
async def close_db(app):
    await app.ctx.redis.close()


@app.put("/data/v1/", name="upload_data")
async def upload_data(request):
    """
    Upload data to the database.
    """
    req = request.json
    for item in req:
        try:
            await request.app.ctx.redis.set(item["id"], item["data"])
        except KeyError as e:
            return response.json({"msg": "upload faild, parameter error: {}".format(str(e))}, status=422)
        except Exception as e:
            return response.json({"msg": "upload faild, error: {}".format(str(e))},  status=400)
    return response.json({"msg": "upload success!"}, status=200)

@app.get("/data/v1/<id>", name="get_data")
async def get_data(request, id):
    """
    Get data from the database.
    """
    id_detail = id.split("-")
    id_detail.append("0") #为了方便处理，添加一个0
    for i, item in enumerate(id_detail):
        if int(item) == 0:
            break;
    pattern = "-".join(id_detail[:i]) + "*"
    keys = await scan_keys(pattern)
    try:
        value = await app.ctx.redis.mget(keys)
        data = assemble_data(keys, value)
    except Exception as e:
        return response.json({"msg": "get data faild, error: {}".format(str(e))}, status=400)
    if data == []:
        return response.json({"msg": "data not found"}, status=410)

    return response.json({"msg":"successfully!","data": data}, status=200)
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port_run, dev=dev)

"""
############################################################################################################
below is the helper function
"""
async def scan_keys(pattern):
    keys = []
    cur = b'0'  # set initial cursor to 0
    while True:
        cur, new_keys = await app.ctx.redis.scan(cur, match=pattern)
        keys.extend(new_keys)
        if cur == 0:
            break
    return keys

def assemble_data(ids, datas):
    result = []
    for id, data in zip(ids, datas):
        result.append({"id": id, "data": float(data)})
    return result