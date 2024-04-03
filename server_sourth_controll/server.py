import sys, os
current_file_dir = os.path.dirname(__file__) # 获取当前文件的父目录
parent_dir = os.path.join(current_file_dir, "../") # 获取父目录
sys.path.append(parent_dir) # 添加父级目录到系统路径,以解决模块导入问题


import httpx
from sanic import Sanic
from sanic.response import json
from user_manage import user_manage_view
from sanic_ext.exceptions import ValidationError

port_run = 10000 # your port number

app = Sanic("sourth_controll")

@app.listener('before_server_start')
async def setup_db(app, loop):
    await app.ctx.db.start(loop)
    app.ctx.client = httpx.AsyncClient() # 创建一个异步HTTP客户端,用于向其他服务发起请求

@app.listener('after_server_stop')
async def close_db(app, loop):
    await app.ctx.client.aclose() # 关闭异步HTTP客户端

app.add_route(user_manage_view.as_view(), "/routing", name= "templete_view")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port_run)