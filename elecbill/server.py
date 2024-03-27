from sanic import Sanic, response
from dbmanage import Database
import pymysql

from routes import initelecbill, elecbill, data
from load_config import *

app = Sanic("elecbillApp")

@app.listener('before_server_start')
async def setup(app, loop):
    """
    Set up before the server starts.
    add the database connection to the app context so that we can access it in HTTPMethodView.
    
    Args:
        app: The Sanic application object.
        loop: The event loop to use for the database connection.
    """

    try:
        app.ctx.db = Database(db['host'], db['port'], db['user'], db['password'], db['database'])
        await app.ctx.db.start(loop)
        await app.ctx.db.init_table()
    except pymysql.err.OperationalError as e:
        print(e)
        print("Please check your database connection")
        exit(1)


@app.listener('after_server_stop')
async def close_db(app, loop):
    await app.ctx.db.stop()


app.add_route(initelecbill.as_view(), "/initelecbill/v1/<id>", name= "initelecbill")
app.add_route(elecbill.as_view(), "/elecbill/v1/<id>", name= "elecbill")
app.add_route(data.as_view(), "/data/v1/<id>", name= "data")


if __name__ == "__main__":
    app.run(host=server['host'], port=server['port'])
