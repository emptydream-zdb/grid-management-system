from sanic.views import HTTPMethodView
from sanic.response import json
from dbmanage import Database

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


class elecbill_id(HTTPMethodView):

    async def get(self, request, id):
        db = request.app.ctx.db
        sql = '''
            SELECT bill FROM elecbill WHERE id = %s
        '''
        res = await db.fetch(sql, id)
        if res == []:
            return json({"msg": "id not exist!"}, status=410)
        else:
            return json({"data": {"elecbill": res[0]}})

    async def delete(self, request, id):
        pass

class elecbill(HTTPMethodView):

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
        pass

    async def get(self, request, id):
        pass
