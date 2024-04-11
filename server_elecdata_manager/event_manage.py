import aiomysql
import datetime

from sanic.views import HTTPMethodView
from sanic.response import json, HTTPResponse

import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "..")) # 添加父级目录到系统路径,以解决模块导入问题

from utils import Database, Snowflake


class DB(Database):
    def __init__(self, host, port, user, password, name):
        super().__init__(host, port, user, password, name)

    async def init_table(self):
        """
        Create the table if it doesn't exist
        """
        query = ["""
        CREATE TABLE IF NOT EXISTS elecbill (
            id VARCHAR(20) NOT NULL PRIMARY KEY,
            bill DOUBLE(16,2) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS elecdata_day (
            uuid BIGINT NOT NULL PRIMARY KEY,
            id VARCHAR(20) NOT NULL,
            data DOUBLE(16,2) NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS elecdata_hour (
            uuid BIGINT NOT NULL PRIMARY KEY,
            id VARCHAR(20) NOT NULL,
            data DOUBLE(16,2) NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
        """]
        await self.execute(query)


class initelecbill(HTTPMethodView):

    async def get(self, request, id):
        db = request.app.ctx.db
        sql = '''
            INSERT INTO elecbill (id, bill) VALUES (%s, %s)
        '''
        if await db.fetch('SELECT id FROM elecbill WHERE id = %s', id) == []:
            await db.execute(sql, (id, 0))
            return json({"message": "data added successfully"})
        else:
            return json({"message": "id already exists"}, status=400)


class elecbill(HTTPMethodView):

    async def get(self, request):
        db = request.app.ctx.db
        sql_equal = '''
            SELECT * FROM elecbill WHERE id = %s
        '''
        sql_like = '''
            SELECT * FROM elecbill WHERE id LIKE %s
        '''
        ids = request.json['id']
        elecbill = {}
        for id in ids:
            res = []
            if id[4:7] == '000':
                res = await db.fetch(sql_like, '{}%'.format(id[:4]))
            else:
                res = await db.fetch(sql_equal, id)
            for item in res:
                if item['id'] not in elecbill:
                    elecbill[item['id']] = item['bill']
        return json({"msg": "successful!", "data":[elecbill]}, status=200)

    async def delete(self, request, id):
        db = request.app.ctx.db
        sql = '''
            DELETE FROM elecbill WHERE id = %s
        '''
        res = await db.fetch("SELECT id FROM elecbill WHERE id = %s", id)
        if res == []:
            return json({"msg": "id not exist!"}, status=410)
        else:
            await db.execute(sql, id)
        return HTTPResponse(status=204)

    async def put(self, request):
        db = request.app.ctx.db
        sql = '''
                UPDATE elecbill SET bill = %s WHERE id = %s
            '''
        req = request.json
        cur = await db.fetch('SELECT bill FROM elecbill WHERE id = %s', req['id'])
        cur = cur[0]['bill']
        if cur == []:
            return json({"msg": "id not exist!"}, status=410)
        else:
            res = cur + req['num']
            await db.execute(sql, (res, req['id']))
        return json({"data":{"elecbill": res}}, status=200)


class data(HTTPMethodView):

    async def post(self, request):
        db = request.app.ctx.db
        sql_day = '''
            INSERT INTO elecdata_day (uuid, id, data) VALUES (%s, %s, %s)
        '''
        sql_hour = '''
            INSERT INTO elecdata_hour (uuid, id, data) VALUES (%s, %s, %s)
        '''
        req = request.json

        # 判断当前时间是否为凌晨12点
        current_time = datetime.datetime.now().time()
        is_hour = False if current_time.hour == 22 else True

        # 生成 uuid
        snowflake = Snowflake(datacenter_id=0, worker_id=0)

        if await db.fetch('SELECT id FROM elecdata_hour WHERE id = %s', req['id']) != []:
            await db.execute(sql_day, (snowflake.generate_uuid(), req['id'], 0))

        sum = 0
        for room in req['data_room']:
            id_prev = room['id'][:8]
            for bed in room['data_beds']:
                await db.execute(sql_hour, (snowflake.generate_uuid(), bed['id'], bed['data']))
            await db.execute(sql_hour, (snowflake.generate_uuid(), room['id'], room['sum']))
            await db.execute(sql_hour, (snowflake.generate_uuid(), "{}005".format(id_prev), room['light']))
            await db.execute(sql_hour, (snowflake.generate_uuid(), "{}006".format(id_prev), room['air']))
            sum += room['sum']
        await db.execute(sql_hour, (snowflake.generate_uuid(), req['id'], sum))

        # 每日23点计算当日用电量总和
        if not is_hour:
            res = await db.fetch("SELECT * FROM elecdata_hour WHERE id LIKE %s", "{}%".format(req['id'][:4]))
            data_day = {}
            for item in res:
                if item['id'] not in data_day:
                    data_day[item['id']] = item['data']
                else:
                    data_day[item['id']] += item['data']
            for key, value in data_day.items():
                await db.execute(sql_day, (snowflake.generate_uuid(), key, value))

        return json({"msg": "data added successfully"}, status=200)

    async def get(self, request, id):
        db = request.app.ctx.db
        sql_like_hour = '''
            SELECT * FROM elecdata_hour WHERE id LIKE %s AND time BETWEEN %s AND %s
        '''
        sql_like_day = '''
            SELECT * FROM elecdata_day WHERE id LIKE %s AND id <> %s AND time BETWEEN %s AND %s
        '''
        sql_equal_hour = '''
            SELECT * FROM elecdata_hour WHERE id = %s AND time BETWEEN %s AND %s
        '''
        sql_equal_day = '''
            SELECT * FROM elecdata_day WHERE id = %s AND time BETWEEN %s AND %s
        '''
        req = request.json
        
        if 'time_start' not in req or 'time_end' not in req:
            # 参数错误
            return json({"msg": "parameter error"}, status=422)
        else:
            # 生成起始日期和结束日期的时间戳
            now = datetime.datetime.now()
            if req['time_start'] and datetime.datetime.strptime(req['time_start'], "%Y-%m-%d") < datetime.datetime(now.year, now.month, now.day):
                time_start = datetime.datetime.strptime(req['time_start'], "%Y-%m-%d")
            else:
                time_start = now - datetime.timedelta(days=1)
            if req['time_end']:
                time_end = datetime.datetime.strptime(req['time_end'], "%Y-%m-%d")
            else:
                time_end = now

        if (await db.fetch(sql_equal_hour, (id, time_start, time_end))) == []:
            # id不存在
            return json({"msg": "id not exist!"}, status=410)
        
        ## 查询数据
        data_detail = []
        data_sub = []
        if id[4:7] == '000' and id[8:] == '000':
            # 查询条件为整栋楼时，返回楼栋和宿舍的数据
            res_this_day = await db.fetch(sql_equal_day, (id, time_start, time_end))
            res_this_hour = await db.fetch(sql_equal_hour, (id, time_start, time_end))
            for item in res_this_hour:
                data_detail.append({'time': item['time'].isoformat(), 'data': item['data']})
            res = await db.fetch(sql_like_day, ('{}%000'.format(id[:4]), '{}000-000'.format(id[:4]), time_start, time_end))
            for item in res:
                data_sub.append({'id': item['id'], 'data_sum': item['data']})
            resp = {'id': id, 'data_sum': res_this_day[0]['data'], 'data_detail': data_detail, 'data_sub': data_sub}
        elif id[4:7] != '000' and id[8:] == '000':
            # 查询条件为宿舍时，返回宿舍和床位的数据
            res_this_day = await db.fetch(sql_equal_day, (id, time_start, time_end))
            res_this_hour = await db.fetch(sql_equal_hour, (id, time_start, time_end))
            for item in res_this_hour:
                data_detail.append({'time': item['time'].isoformat(), 'data': item['data']})
            res = await db.fetch(sql_like_day, ('{}%'.format(id[:8]), '{}000'.format(id[:8]), time_start, time_end))
            for item in res:
                data_sub.append({'id': item['id'], 'data_sum': item['data']})
            resp = {'id': id, 'data_sum': res_this_day[0]['data'], 'data_detail': data_detail, 'data_sub': data_sub}
        else:
            # 查询条件为床位时，返回床位的数据
            res_this_day = await db.fetch(sql_equal_day, (id, time_start, time_end))
            res_this_hour = await db.fetch(sql_equal_hour, (id, time_start, time_end))
            for item in res_this_hour:
                data_detail.append({'time': item['time'].isoformat(), 'data': item['data']})
            resp = {'id': id, 'data_sum': res_this_day[0]['data'], 'data_detail': data_detail, 'data_sub': []}
        return json({"data": resp}, status=200)
