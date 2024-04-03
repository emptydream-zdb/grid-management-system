import jsonschema

class Server:
    async def parm_verify(self, req: dict):
        schema = {
            "type" : "object",
            "properties" : {
                "id_user" : {"type" : "string", "minLength": 1, "maxLength": 20},
                "id_room" : {
                    "type" : "string", 
                    "pattern": "^[0-9]+-[0-9]+-[0-9]+$"
                },
                "name" : {"type" : "string", "minLength": 1, "maxLength": 20},
                "password" : {"type" : "string", "minLength": 1, "maxLength": 255},
                "group" : {"type" : "string", "minLength": 1, "maxLength": 20},
                "work_unit" : {"type" : "string", "minLength": 1, "maxLength": 255},
            },
            "required": ["id_user", "id_room", "name", "password", "group", "work_unit"]
        }

        try:
            jsonschema.validate(req, schema)
        except jsonschema.exceptions.ValidationError as e:
            return False, str(e)
        return True, "Valid parameters"