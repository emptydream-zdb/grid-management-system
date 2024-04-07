from sanic import Sanic, response
from dbmanage import DB
import pymysql
import datetime

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
        app.ctx.db = DB(db['host'], db['port'], db['user'], db['password'], db['name'])
        await app.ctx.db.start(loop)
        await app.ctx.db.init_table()
        
    except pymysql.err.OperationalError as e:
        print(e)
        print("Please check your database connection")
        exit(1)


@app.listener('after_server_stop')
async def close_db(app, loop):
    await app.ctx.db.stop()


app.add_route(deviceRegistration.as_view(), "/device/registration/v1/<id>", name = "device-registration")
app.add_route(deviceVerification.as_view(), "/device/verification/v1/<id>", name = "device-verification")
app.add_route(device.as_view(), "/device/v1/<id>", name = "device")
app.add_route(switch.as_view(), "/switch/v1/<reason>", name = "switch")


if __name__ == "__main__":
    app.run(host=server['host'], port=server['port'], dev=True)
