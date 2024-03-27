from sanic import Sanic
from sanic.response import json
from utils import Database

from templete_view import templete_view

port_run = 10000 # your port number

app = Sanic("templete_view")

@app.listener('before_server_start')
async def setup_db(app, loop):
    """
    Set up the database connection before the server starts.
    add the database connection to the app context so that we can access it in HTTPMethodView.
    
    Args:
        app: The Sanic application object.
        loop: The event loop to use for the database connection.
    """
    user = "<your_user_name>"
    password = "<your_password>"
    database = "<your_database_name>"
    app.ctx.db = Database("127.0.0.1", 3306, user, password, database)
    await app.ctx.db.start(loop)

@app.listener('after_server_stop')
async def close_db(app, loop):
    await app.ctx.db.stop()

app.add_route(templete_view.as_view(), "/routing", name= "templete_view")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port_run)