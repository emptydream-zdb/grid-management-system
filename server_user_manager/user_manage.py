from sanic.views import HTTPMethodView
from sanic.response import json, HTTPResponse

async def init_table(app) -> None:
        """
        Initializes the 'user' table in the database if it doesn't already exist.
        Args:
            request: The request object.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS user (
                id_user VARCHAR(20) PRIMARY KEY,
                id_room VARCHAR(20),
                name VARCHAR(20) NOT NULL,
                password VARCHAR(255) NOT NULL,
                user_group VARCHAR(20) NOT NULL,
                work_unit VARCHAR(255) NOT NULL
            );
        """
        await app.ctx.db.execute(sql)

class user_manager_view(HTTPMethodView):

    async def post(self, request):
        """
        add a user to the database
        """
        req = request.json
        sql = "SELECT id_room FROM user WHERE id_user = %s"
        result = await request.app.ctx.db.fetch(sql, args=(req["id_user"]))
        if result != []:
            return json({"msg": "User already exist"}, status=400)
        sql = """
            INSERT INTO user (id_user, id_room, name, password, user_group, work_unit)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        try:
            await request.app.ctx.db.execute(sql, args=(req["id_user"], req["id_room"], req["name"], req["password"], req["group"], req["work_unit"]))
        except Exception as e:
            return json({"msg": "User not added, error:{}".format(str(e))}, status=400)
        return json({"msg": "User added successfully"})
    
    async def get(self, request, id):
        """
        get a user or it's password from the database
        """
        req = request.json
        if request.args.get("class") == "user":            
            if request.args.get("passwd") != None:
                sql = "SELECT password FROM user WHERE id_user = %s"
                try:
                    result = await request.app.ctx.db.fetch(sql, args=(id))
                except Exception as e:
                    return json({"msg": "User not found, error:{}".format(str(e))}, status=400)
                return json({"msg":"success!","data": result[0][0]})
            else:
                sql = "SELECT * FROM user WHERE id_user = %s"
                try:
                    result = await request.app.ctx.db.fetch(sql, args=(id))
                except Exception as e:
                    return json({"msg": "query fail, error:{}".format(str(e))}, status=400)
                if result == []:
                    return json({"msg": "User not found"}, status=400)
                for x in result:
                    x["group"] = x["user_group"]
                    del x["user_group"]
                return json({"msg":"success!","data": result})
        else:
            sql = "SELECT * FROM user WHERE id_room = %s"
            try:
                result = await request.app.ctx.db.fetch(sql, args=(id))
            except Exception as e:
                return json({"msg": "query fail, error:{}".format(str(e))}, status=400)
            if result == []:
                return json({"msg": "User not found"}, status=400)
            return json({"msg":"success!","data": result})
    
    async def delete(self, request):
        """
        TODO: delete a user from the database
        """
        req = request.json
        sql = "SELECT password FROM user WHERE id_user = %s"
        try:
            result = await request.app.ctx.db.fetch(sql, args=[(req["id_user"])])
        except Exception as e:
            return json({"msg": "delete, error:{}".format(str(e))}, status=400)
        
        if result == []:
            return json({"msg": "User not exist"}, status=400)
        
        if result[0]["password"] != req["password"]:
            return json({"msg": "Password error"}, status=400)
        
        sql = "DELETE FROM user WHERE id_user = %s"
        try:
            await request.app.ctx.db.execute(sql, args=(req["id_user"]))
        except Exception as e:
            return json({"msg": "User not deleted, error:{}".format(str(e))}, status=400)
        return HTTPResponse(status=204)
    
    async def put(self, request, id):
        """
        update a user in the database
        """
        req = request.json
        sql = "SELECT password FROM user WHERE id_user = %s"
        try:
            result = await request.app.ctx.db.fetch(sql, args=[(id)])
        except Exception as e:
            return json({"msg": "update fail!, error:{}".format(str(e))}, status=400)
        if result == []:
            return json({"msg": "User not exist"}, status=400)
        if req.get("group") != None:
            req["user_group"] = req["group"]
            del req["group"]
        update_items = []
        args = []
        for key, value in req.items():
            update_items.append(f"{key} = %s")
            args.append(value)
        update_str = ", ".join(update_items)
        args.append(id)
        sql = f"UPDATE user SET {update_str} WHERE id_user = %s"
        try:
            await request.app.ctx.db.execute(sql, args=tuple(args))
        except Exception as e:
            return json({"msg": "User not updated, error:{}".format(str(e))}, status=400)
        return json({"msg": "User updated successfully"})



    