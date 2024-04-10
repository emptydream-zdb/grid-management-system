from sanic import Sanic, response
from sanic import Websocket, Request

import pymysql
import datetime
import jwt

from event_manage import *
from load_config import *

app = Sanic("elecbillApp")

@app.middleware("response")
async def add_csp(request, response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Request-Headers"] = "*"

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


@app.middleware('request')
async def custom_middleware(request):
    if request.path.startswith("/hb/<token>"):
        try:
            queries = request.args
            token = queries['token'][0]
            id = queries['id'][0]

            db = app.ctx.db
            db.execute("SELECT * FROM device WHERE id = %s", (id))
            if device == []:
                return response.json({"error": "Device not found"}, status=410)
            
            decoded_token = jwt.decode(token, password, algorithms=['HS256'], verify=False)
            if decoded_token['id'] != id:
                return response.json({"error": "Invalid token"}, status=401)

            return None

        except Exception as e:
            return response.json({"error": "Invalid request"}, status=400)


app.add_route(deviceRegistration.as_view(), "/device/registration/v1/<id>", name = "device-registration")
app.add_route(deviceVerification.as_view(), "/device/verification/v1/<id>", name = "device-verification")
app.add_route(device.as_view(), "/device/v1/<id>", name = "device_id", methods = ['PUT', 'DELETE'])
app.add_route(device.as_view(), "/device/v1", name = "device", methods = ['GET'])
app.add_websocket_route(heartbeat, '/hb')
# app.add_websocket(, '/')



if __name__ == "__main__":
    app.run(host=server['host'], port=server['port'], dev=True)
