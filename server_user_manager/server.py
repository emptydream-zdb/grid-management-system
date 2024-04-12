import sys, os
current_file_dir = os.path.dirname(__file__) # 获取当前文件的父目录
parent_dir = os.path.join(current_file_dir, "../") # 获取父目录
sys.path.append(parent_dir) # 添加父级目录到系统路径,以解决模块导入问题


from sanic import Sanic
from sanic.response import json
from sanic import Request
from utils import Database
from user_manage import user_manager_view, init_table

app = Sanic("user_manager")
app.update_config(os.path.join(current_file_dir, "sanic_config.conf")) # 从配置文件中加载配置

@app.listener('before_server_start')
async def setup_db(app: Sanic, loop):
    """
    Set up the database connection before the server starts.
    add the database connection to the app context so that we can access it in HTTPMethodView.
    
    Args:
        app: The Sanic application object.
        loop: The event loop to use for the database connection.
    """
    app.ctx.db = Database("127.0.0.1", 3306, app.config.DB_USER, app.config.DB_PWD, app.config.DATABASE)
    await app.ctx.db.start(loop)
    await init_table(app)

@app.listener('after_server_stop')
async def close_db(app, loop):
    await app.ctx.db.stop()

app.add_route(user_manager_view.as_view(), "/user/v1", methods=['POST', 'PUT'], name="user_manager")
app.add_route(user_manager_view.as_view(), "/user/v1/<id>", methods=['GET', 'DELETE'], name="user_manager_id")

if __name__ == "__main__":
    app.run(host=app.config.HOST, port=app.config.PORT, dev=app.config.DEV)