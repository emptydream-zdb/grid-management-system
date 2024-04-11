from sanic import Sanic, response
import pymysql
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from event_manage import *
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

        # 创建一个定期任务
        scheduler = AsyncIOScheduler()
        scheduler.add_job(delete_old_data, 'cron', day=1)
        scheduler.start()
    except pymysql.err.OperationalError as e:
        print(e)
        print("Please check your database connection")
        exit(1)


# 定义一个定期任务，删除上上个月的数据
async def delete_old_data():
    today = datetime.date.today()
    one_months_ago = datetime.date(today.year, today.month, 1) - datetime.timedelta(days=30)
    db = app.ctx.db
    # 执行SQL命令来删除指定时间段内的数据
    await db.execute("DELETE FROM elecdata_hour WHERE time < %s", one_months_ago)


@app.listener('after_server_stop')
async def close_db(app, loop):
    await app.ctx.db.stop()


app.add_route(initelecbill.as_view(), "/initelecbill/v1/<id>", name= "initelecbill")
app.add_route(elecbill.as_view(), "/elecbill/v1/<id>", name= "elecbill_id", methods=['DELETE'])
app.add_route(elecbill.as_view(), "/elecbill/v1/", name= "elecbill", methods=['PUT', 'POST'])
app.add_route(data.as_view(), "/data/v1/<id>", name= "data", methods=['PUT'])
app.add_route(data.as_view(), "/data/v1/", name= "data_id", methods=['POST'])


if __name__ == "__main__":
    app.run(host=server['host'], port=server['port'], dev=False)
