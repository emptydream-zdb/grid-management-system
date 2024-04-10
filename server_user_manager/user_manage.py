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
        add multiple users to the database
        """
        req = request.json
        sql_check = "SELECT id_user FROM user WHERE id_user IN(%s)"
        sql_check = sql_check % ", ".join(["%s"]*len(req))
        id_users = [item["id_user"] for item in req]
        result = await request.app.ctx.db.fetch(sql_check, args=tuple(id_users))
        if result != []:
            existing_users = [item['id_user'] for item in result]
            return json({"msg": "Some users already exist", "existing_users": existing_users}, status=400)
        
        sql_insert = """
            INSERT INTO user (id_user, id_room, name, password, user_group, work_unit)
            VALUES %s;
        """
        sqls = []
        args = []
        for i in range(0, len(req), 1000): # Split the data into chunks of 1000 items each
            arg = []
            chunk = req[i:i+1000]
            values = ', '.join(["(%s, %s, %s, %s, %s, %s)"] *len(chunk))
            sqls.append(sql_insert % values)

            for item in chunk:
                arg.extend([item["id_user"], item["id_room"], item["name"], item["password"], item["group"], item["work_unit"]])
            args.append(tuple(arg))
        try:           
            await request.app.ctx.db.execute(sqls, args=args)
        except Exception as e:
            return json({"msg": "Users not added, error:{}".format(str(e))}, status=400)
        return json({"msg": "Users added successfully"})
    
    async def get(self, request, id):
        """
        get a user or it's password from the database
        """
        req = request.json
        if request.args.get("class") == "user":            
            if request.args.get("passwd") == "true":
                sql = "SELECT password, user_group, id_room FROM user WHERE id_user = %s"
                try:
                    result = await request.app.ctx.db.fetch(sql, args=(id))
                except Exception as e:
                    return json({"msg": "User not found, error:{}".format(str(e))}, status=400)
                if result == []:
                    return json({"msg": "User not found"}, status=410)
                
                result[0]["group"] = result[0]["user_group"]
                del result[0]["user_group"]
                result = result[0]
                return json(result, status=201)
            else:
                sql = "SELECT id_user, id_room, name, user_group, work_unit FROM user WHERE id_user = %s"
                try:
                    result = await request.app.ctx.db.fetch(sql, args=(id))
                except Exception as e:
                    return json({"msg": "query fail, error:{}".format(str(e))}, status=400)
        else:
            id_detail = id.split("-")
            id_detail.append("0") #为了方便处理，添加一个0
            for i, item in enumerate(id_detail):
                if int(item) == 0:
                    break;
            pattern = "-".join(id_detail[:i]) + "%"
            sql = "SELECT * FROM user WHERE id_room LIKE %s ORDER BY id_room ASC, id_user ASC"
            try:
                result = await request.app.ctx.db.fetch(sql, args=(pattern))
            except Exception as e:
                return json({"msg": "query fail, error:{}".format(str(e))}, status=400)
        if result == []:
            return json({"msg": "User not found"}, status=410)
        for x in result:
            x["group"] = x["user_group"]
            del x["user_group"]
        return json({"msg":"success!","data": result})
    
    async def delete(self, request, id):
        """
        TODO: delete a user from the database
        """
        req = request.json
        sql = "SELECT password FROM user WHERE id_user = %s"
        try:
            result = await request.app.ctx.db.fetch(sql, args=(id))
        except Exception as e:
            return json({"msg": "delete error:{}".format(str(e))}, status=400)
        
        if result == []:
            return json({"msg": "User not exist"}, status=410)
        
        sql = "DELETE FROM user WHERE id_user = %s"
        try:
            await request.app.ctx.db.execute(sql, args=(id))
        except Exception as e:
            return json({"msg": "User not deleted, error:{}".format(str(e))}, status=400)
        return HTTPResponse(status=204)
    
    async def put(self, request):
        """
        update multiple users in the database
        """
        req = request.json
        sql_check = "SELECT id_user FROM user WHERE id_user IN (%s)"
        sql_check = sql_check % ", ".join(["%s"]*len(req))
        id_users = [item["id_user"] for item in req]
        result = await request.app.ctx.db.fetch(sql_check, tuple(id_users))
        existing_users = [item['id_user'] for item in result]
        non_existing_users = list(set(id_users) - set(existing_users))
        if non_existing_users != []:
            return json({"msg": "Some users do not exist", "non_existing_users": non_existing_users}, status=410)

        updates = []
        args = []
        for item in req:
            if item.get("group") != None:
                item["user_group"] = item["group"]
                del item["group"]
            update_items = []
            arg = []
            for key, value in item.items():
                if key != "id_user":
                    update_items.append(f"{key} = %s")
                    arg.append(value)
            update_str = ", ".join(update_items)
            arg.append(item["id_user"])
            updates.append(f"UPDATE user SET {update_str} WHERE id_user = %s")
            args.append(tuple(arg))
        try:
            await request.app.ctx.db.execute(updates, args=args)
        except Exception as e:
            return json({"msg": "Users not updated, error:{}".format(str(e))}, status=400)
        return json({"msg": "Users updated successfully"})



    