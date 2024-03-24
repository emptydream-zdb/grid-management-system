from sanic import Sanic
from sanic.response import json
from sanic import Request
from dbmanage import Database
import sys

from templete_view import templete_view

host = sys.argv[1]
port = sys.argv[2]
user = sys.argv[3]
password = sys.argv[4]
database = sys.argv[5]


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
    app.ctx.db = Database(host, port, user, password, database)
    await app.ctx.db.start(loop)

@app.listener('after_server_stop')
async def close_db(app, loop):
    await app.ctx.db.stop()

app.add_route(templete_view.as_view(), "/routing", name= "templete_view")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)