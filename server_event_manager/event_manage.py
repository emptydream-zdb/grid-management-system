from sanic.response.types import JSONResponse
from sanic.views import HTTPMethodView
from sanic.response import json, HTTPResponse
from utils import Snowflake

snowflake = Snowflake(datacenter_id=0, worker_id=3)

async def init_table(app) -> None:
        """
        Initializes the 'event' table in the database if it doesn't already exist.
        Args:
            request: The request object.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS event (
                id_event BIGINT PRIMARY KEY,
                id_room VARCHAR(20) NOT NULL,
                id_initiator VARCHAR(20) NOT NULL,
                time_start VARCHAR(25) NOT NULL,
                time_end VARCHAR(25) DEFAULT '',
                event VARCHAR(255) NOT NULL,
                result VARCHAR(255) DEFAULT '',
                state VARCHAR(10) NOT NULL,
                id_processor VARCHAR(20) DEFAULT ''
            );
        """
        await app.ctx.db.execute(sql)

def gen_event_id() -> str:
    """
    Generate a unique id for the event.
    """
    return snowflake.generate_uuid()

class event_manager_view(HTTPMethodView):

    async def post(self, request) -> JSONResponse:
        req = request.json
        sql = """
            SELECT COUNT(*) FROM event WHERE id_room = %s AND event = %s AND state = 'pending';
        """
        try:
             result = await request.app.ctx.db.fetch(sql, (req["id_room"], req["event"]))
        except Exception as e:
            return json({"msg": "Event add fail, error: {}".format(str(e))}, status=400)
        if result[0]["COUNT(*)"] > 0:
            return json({"msg": "Do not add events repeatedly!"}, status=400)
        sql = """
            INSERT INTO event (id_event, id_room, id_initiator, time_start, event, state)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        try:
            await request.app.ctx.db.execute(sql, (gen_event_id(), req["id_room"], req["id_initiator"], req["time_start"], req["event"], req["state"]))
        except Exception as e:
            return json({"msg": "Event add fail, error: {}".format(str(e))}, status=400)
        return json({"msg": "Event added successfully"})
    
    async def get(self, request, id) -> JSONResponse:
        limit = request.args.get("num")
        state = request.args.get("state")

        id_detail = id.split("-")
        id_detail.append("0") #为了方便处理，添加一个0
        for i, item in enumerate(id_detail):
            if int(item) == 0:
                break;
        pattern = "-".join(id_detail[:i]) + "%"
        if limit is None or limit == "":
            if state is None or state == "":
                sql = """
                    SELECT * FROM event WHERE id_room LIKE %s ORDER BY state ASC, id_event DESC;
                """
                try:
                    result = await request.app.ctx.db.fetch(sql, (pattern))
                except Exception as e:
                    return json({"msg": "Get event fail, error: {}".format(str(e))}, status=400)
            else:
                sql = """
                    SELECT * FROM event WHERE id_room LIKE %s AND state = %s ORDER BY id_event DESC;
                """
                try:
                    result = await request.app.ctx.db.fetch(sql, (pattern, state))
                except Exception as e:
                    return json({"msg": "Get event fail, error: {}".format(str(e))}, status=400)
            
        else:
            limit = int(limit)
            if state is None or state == "":
                sql = """
                    SELECT * FROM event WHERE id_room LIKE %s ORDER BY state ASC, id_event DESC LIMIT %s;
                """
                try:
                    result = await request.app.ctx.db.fetch(sql, (pattern, limit))
                except Exception as e:
                    return json({"msg": "Get event fail, error: {}".format(str(e))}, status=400)
            else:
                sql = """
                    SELECT * FROM event WHERE id_room LIKE %s AND state = %s ORDER BY id_event DESC LIMIT %s;
                """
                try:
                    result = await request.app.ctx.db.fetch(sql, (pattern, state, limit))
                except Exception as e:
                    return json({"msg": "Get event fail, error: {}".format(str(e))}, status=400)
        for item in result:
            item["id_event"] = str(item["id_event"])
        return json({"msg": "successfully", "data": result})

    
    async def put(self, request, id) -> JSONResponse:
        req = request.json
        sql = """
            SELECT COUNT(*) FROM event WHERE id_event = %s;
        """
        id = int(id)
        try:
            result = await request.app.ctx.db.fetch(sql, (id,))
        except Exception as e:
            return json({"msg": "Event update fail, error: {}".format(str(e))}, status=400)
        if result[0]["COUNT(*)"] == 0:
            return json({"msg": "Event not exist!"}, status=410)
        sql = """
            UPDATE event SET time_end = %s, result = %s, state = %s, id_processor = %s WHERE id_event = %s;
        """
        try:
            await request.app.ctx.db.execute(sql, (req["time_end"], req["result"], req["state"], req["id_processor"], id))
        except Exception as e:
            return json({"msg": "Event update fail, error: {}".format(str(e))}, status=400)
        return json({"msg": "Event update successfully"})
    
    async def delete(self, request, id) -> JSONResponse:
        sql = """
            SELECT state FROM event WHERE id_event = %s;
        """
        id = int(id)
        try:
            result = await request.app.ctx.db.fetch(sql, (id,))
        except Exception as e:
            return json({"msg": "Event delete fail, error: {}".format(str(e))}, status=400)
        if len(result) == 0:
            return json({"msg": "Event not exist!"}, status=410)
        if result[0]["state"] == "processed":
            return json({"msg": "Processed events cannot be deleted!"}, status=405)
        sql = """
            DELETE FROM event WHERE id_event = %s;
        """
        try:
            await request.app.ctx.db.execute(sql, (id,))
        except Exception as e:
            return json({"msg": "Event delete fail, error: {}".format(str(e))}, status=400)
        return HTTPResponse(status=204)
        