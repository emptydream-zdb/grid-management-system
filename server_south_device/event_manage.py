import aiomysql

from sanic.views import HTTPMethodView
from sanic.response import json, HTTPResponse

import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "..")) # 添加父级目录到系统路径,以解决模块导入问题

from utils import Database

import requests


class DB(Database):
    def __init__(self, host, port, user, password, name):
        super().__init__(host, port, user, password, name)

    async def init_table(self):
        """
        Create the table if it doesn't exist
        """
        query = ["""
        CREATE TABLE IF NOT EXISTS devices (
            id VARCHAR(20) NOT NULL PRIMARY KEY,
            salt VARCHAR(150) NOT NULL,
            state VARCHAR(20) NOT NULL,
            hardware_sn VARCHAR(50) NOT NULL,
            hardware_model VARCHAR(50) NOT NULL,
            software_base_version VARCHAR(50) NOT NULL,
            software_base_lastUpdate VARCHAR(50) NOT NULL,
            software_base_status VARCHAR(20) NOT NULL,
            software_work_version VARCHAR(50) NOT NULL,
            software_work_lastUpdate VARCHAR(50) NOT NULL,
            software_work_status VARCHAR(20) NOT NULL,
            nic_eth_mac VARCHAR(50) NOT NULL,
            nic_eth_ipv4 VARCHAR(50) NOT NULL,
            nic_wifi_mac VARCHAR(50) NOT NULL,
            nic_wifi_ipv4 VARCHAR(50) NOT NULL
        )
        """]
        await self.execute(query)


import jwt
import random
import string

def generate_random_password(length):
    """
    Generate a random password of the specified length.

    Parameters:
    length (int): The length of the password to generate.

    Returns:
    str: The randomly generated password.
    """
    letters = string.ascii_letters + string.digits
    password = ''.join(random.choice(letters) for _ in range(length))
    return password


def generate_salt(id, password):
    """
    Generate a salt using the given id and password.

    Args:
        id (int): The user's ID.
        password (str): The user's password.

    Returns:
        str: The generated salt.

    """
    salt = jwt.encode({'id': id, 'password': password}, 'secret_key', algorithm='HS256')
    return salt


class deviceRegistration(HTTPMethodView):
    async def post(self, request, id):
        """
        Register a device with the given id.
        
        Args:
            request: The request object.
            id: The device id.
        
        Returns:
            A JSON response with the status of the registration.
        """
        req = request.json
        db = request.app.ctx.db
        sql = '''
            INSERT INTO devices (id, salt, state, hardware_sn, hardware_model, software_base_version,
            software_base_lastUpdate, software_base_status, software_work_version, software_work_lastUpdate,
            software_work_status, nic_eth_mac, nic_eth_ipv4, nic_wifi_mac, nic_wifi_ipv4) VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        '''
        try:
            if await db.fetch('SELECT id FROM devices WHERE id = %s', id) != []:
                return json({"msg": "Device already registered"}, status=410)

            password = generate_random_password(16)
            salt = generate_salt(id, password)
            resp = {
                "msg": "Device registered successfully",
                "data": {
                    "id": id,
                    "password": password
                }
            }
            for key, value in req.items():
                resp["data"][key] = value
            await db.execute(sql, (id, salt, req['state'], req['hardware']['sn'], req['hardware']['model'],
                                   req['software']['base']['version'], req['software']['base']['lastUpdate'],
                                   req['software']['base']['status'], req['software']['work']['version'],
                                   req['software']['work']['lastUpdate'], req['software']['work']['status'],
                                   req['nic']['eth']['mac'], req['nic']['eth']['ipv4'], req['nic']['wifi']['mac'],
                                   req['nic']['wifi']['ipv4']))
                        
            return json(resp, status=200)
        
        except Exception as e:
            return json({"status": "failed", "error": str(e)}, status=400)


import time
class deviceVerification(HTTPMethodView):
    async def post(self, request, id):
        """
        Verify a device with the given id.
        
        Args:
            request: The request object.
            id: The device id.
        
        Returns:
            A JSON response with the status of the verification.
        """
        try:
            db = request.app.ctx.db
            device = await db.fetch("SELECT * FROM devices WHERE id = %s", id)
            if device == []:
                return json({"msg": "Device not found"}, status=410)
            device = device[0]
            salt = device['salt']
            password = request.json['password']
            if salt != generate_salt(id, password):
                return json({"msg": "Invalid password"}, status=401)

            headers = {
                'alg': 'HS256',
                'typ': 'JWT'
            }

            timeout = 3600  # 1 hour
            payload = {
                'id': id,
                'exp': int(time.time() + timeout)
            }
            
            token = jwt.encode(payload=payload, key=salt, algorithm='HS256', headers=headers)
            
            return json({"data":{"token":token}})
        
        except Exception as e:
            return json({"status": "failed", "error": str(e)}, status=400)


class device(HTTPMethodView):
    async def put(self, request, id):
        """
        Update the device with the given id.
        
        Args:
            request: The request object.
            id: The device id.
        
        Returns:
            A JSON response with the status of the update.
        """
        db = request.app.ctx.db
        req = request.json
        
        try:
            device = await db.fetch("SELECT * FROM devices WHERE id = %s", id)
            if device == []:
                return json({"msg": "Device not found"}, status=410)

            # Flatten the nested JSON structure
            flat_device = {}
            for key, value in device[0].items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        flat_device[sub_key] = sub_value
                else:
                    flat_device[key] = value

            # Compare flat_device and req to find different values
            diff_values = {}
            for key, value in req.items():
                if key in flat_device and flat_device[key] != value:
                    diff_values[key] = value

            # Update the device with the different values
            if diff_values:
                set_values = ", ".join([f"{key} = %s" for key in diff_values])
                await db.execute("UPDATE devices SET {} WHERE id = %s".format(set_values), (*diff_values.values(), id))
            
            return json({"status": "success"})
        
        except Exception as e:
            return json({"status": "failed", "error": str(e)}, status=400)

    async def delete(self, request, id):
        """
        Delete the device with the given id.
        
        Args:
            request: The request object.
            id: The device id.
        
        Returns:
            A JSON response with the status of the deletion.
        """
        db = request.app.ctx.db
        try:
            if await db.fetch("SELECT id FROM devices WHERE id = %s", id) == []:
                return json({"msg": "Device not found"}, status=410)
            await db.execute("DELETE FROM devices WHERE id = %s", id)
            return HTTPResponse(status=204)
        
        except Exception as e:
            return json({"status": "failed", "error": str(e)}, status=400)

    async def get(self, request):
            """
            Handle GET requests to retrieve device information.

            Args:
                request: The request object containing the query parameters.

            Returns:
                A JSON response containing the device information.

            Raises:
                HTTPException: If there is an error processing the request.
            """
            db = request.app.ctx.db
            queries = request.args
            
            try:
                if 'id' in queries:
                    device = await db.fetch("SELECT * FROM devices WHERE id = %s", queries['id'])
                    if device == []:
                        return json({"msg": "Device not found"}, status=410)
                    device = device[0]  # Get the first device from the result
                else:
                    return json({"errorcode": 1, "msg": "no query"}, status=400)

                nested_device = {
                    "id": device["id"],
                    "state": device["state"],
                    "hardware": {
                        "sn": device["hardware_sn"],
                        "model": device["hardware_model"]
                    },
                    "software": {
                        "base": {
                            "version": device["software_base_version"],
                            "lastUpdate": device["software_base_lastUpdate"],
                            "status": device["software_base_status"]
                        },
                        "work": {
                            "version": device["software_work_version"],
                            "lastUpdate": device["software_work_lastUpdate"],
                            "status": device["software_work_status"]
                        }
                    },
                    "nic": {
                        "eth": {
                            "mac": device["nic_eth_mac"],
                            "ipv4": device["nic_eth_ipv4"]
                        },
                        "wifi": {
                            "mac": device["nic_wifi_mac"],
                            "ipv4": device["nic_wifi_ipv4"]
                        }
                    }
                }

                return json(nested_device)
            
            except Exception as e:
                return json({"status": "failed", "error": str(e)}, status=400)


from sanic import Websocket, Request
import asyncio
import json as json_module

async def heartbeat(request, ws):
    """
    Handle the heartbeat request.

    Args:
        request: The request object.
        ws: The websocket object.

    Returns:
        A JSON response with the status of the heartbeat.
    """
    while True:
        try:
            data = await asyncio.wait_for(ws.recv(), timeout=60)
            data_json = json_module.loads(data)
            if data_json.get("type") == "heartbeat":
                await ws.send("heartbeat received")
            elif data_json.get("type") == "upload":

                await ws.send("upload successful")
            elif data_json.get("type") == "close":
                await ws.send("closing connection")
                break
            else:
                await ws.send("invalid request")
        except asyncio.TimeoutError:
            await ws.send("timeout")
            break
