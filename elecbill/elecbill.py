from sanic.views import HTTPMethodView
from sanic.response import json
from dbmanage import Database

class initelecbill(HTTPMethodView):

    async def get(self, request, id):
        db = request.app.ctx.db
        sql = '''
            INSERT INTO users (id, elecbill)
            VALUES (?, ?)
        '''
        if not db.fetch('SELECT item FROM id WHERE item = ?', (id,)):
            db.execute([sql], (id, 0))
            return json({"message": "User added successfully"})
        else:
            return json({"message": "id already exists"}, status=400)


class elecbill(HTTPMethodView):

    async def get(self, request, id):
        pass
    
    async def put(self, request, id):
        pass

    async def delete(self, request, id):
        pass


class data(HTTPMethodView):
    
    async def post(self, request):
        pass

    async def get(self, request, id):
        pass
