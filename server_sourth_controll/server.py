import sys, os
current_file_dir = os.path.dirname(__file__) # 获取当前文件的父目录
parent_dir = os.path.join(current_file_dir, "../") # 获取父目录
sys.path.append(parent_dir) # 添加父级目录到系统路径,以解决模块导入问题


import httpx
from sanic import Sanic
from sanic.response import json
from user_manage import user_manage_view
from event_manage import event_manage_view
from data_bill_manage import elecbill_manage_view, get_elec_used_data, get_elec_real_data
from authorize import login, refresh


app = Sanic("sourth_controll")

app.update_config(os.path.join(current_file_dir, "sanic_config.conf")) # 从配置文件中加载配置

@app.listener('before_server_start')
async def setup_db(app, loop):
    app.ctx.client = httpx.AsyncClient() # 创建一个异步HTTP客户端,用于向其他服务发起请求

@app.listener('after_server_stop')
async def close_db(app, loop):
    await app.ctx.client.aclose() # 关闭异步HTTP客户端

# 添加用户管理相关API路由
app.add_route(user_manage_view.as_view(), "/user/v1", methods=['POST', 'PUT'], name= "user_manage")
app.add_route(user_manage_view.as_view(), "/user/v1/<id>", methods=['GET', 'DELETE'], name= "user_manage_id")

app.add_route(event_manage_view.as_view(), "/event/v1", methods=['POST'], name= "event_manage")
app.add_route(event_manage_view.as_view(), "/event/v1/<id>", methods=['GET', 'DELETE', 'PUT'], name= "event_manage_id")

app.add_route(elecbill_manage_view.as_view(), "/elecbill/v1/<room_id>", methods=['GET', 'PUT', 'DELETE'], name= "data_manage_id")
app.add_route(get_elec_used_data, "/data/used/v1/<room_id>", methods=['GET'], name= "elec_used_data")
app.add_route(get_elec_real_data, "/data/real/v1/<room_id>", methods=['GET'], name= "elec_real_data")

app.add_route(login, "/login/v1", methods=['PUT'], name= "login")
app.add_route(refresh, "/refresh/v1", methods=['GET'], name= "refresh")

if __name__ == "__main__":
    app.run(host=app.config.HOST, port=app.config.PORT, dev = app.config.DEV)