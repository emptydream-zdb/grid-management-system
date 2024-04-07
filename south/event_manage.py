import aiomysql

from sanic.views import HTTPMethodView
from sanic.response import json, HTTPResponse

import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "..")) # 添加父级目录到系统路径,以解决模块导入问题

from utils import Database


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
            bill DOUBLE(16,2) NOT NULL
        )
        """]
        await self.execute(query)
{
    "state": "normal",
    "hardware": {
        "sn": "fugiat",
        "model": "ipsum sunt do"
    },
    "software": {
        "base": {
            "version": "et mollit Lorem",
            "lastUpdate": "2004-01-14",
            "status": "consectetur"
        },
        "work": {
            "version": "enim dolor deserunt fugiat",
            "lastUpdate": "2003-08-14",
            "status": "eiusmod dolor minim"
        }
    },
    "nic": {
        "eth": {
            "mac": "voluptate",
            "ipv4": "exercitation consectetur aute adipisicing"
        },
        "wifi": {
            "mac": "tempor",
            "ipv4": "dolore dolore voluptate"
        }
    }
}


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
        
        try:
            await request.app.ctx.db.register_device(id)
            return json({"status": "success"})
        
        except Exception as e:
            return json({"status": "failed", "error": str(e)}, status=400)


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
            await request.app.ctx.db.verify_device(id)
            return json({"status": "success"})
        
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
        
        try:
            await request.app.ctx.db.update_device(id, request.json)
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
        
        try:
            await request.app.ctx.db.delete_device(id)
            return json({"status": "success"})
        
        except Exception as e:
            return json({"status": "failed", "error": str(e)}, status=400)

    async def get(self, request, id):
        """
        Get the device with the given id.
        
        Args:
            request: The request object.
            id: The device id.
        
        Returns:
            A JSON response with the device information.
        """
        
        try:
            device = await request.app.ctx.db.get_device(id)
            return json(device)
        
        except Exception as e:
            return json({"status": "failed", "error": str(e)}, status=400)


class switch(HTTPMethodView):
    async def get(self, request, reason):
        """
        Switch the device based on the given reason.
        
        Args:
            request: The request object.
            reason: The reason for switching the device.
        
        Returns:
            A JSON response with the status of the switch.
        """
        
        try:
            await request.app.ctx.db.switch_device(reason)
            return json({"status": "success"})
        
        except Exception as e:
            return json({"status": "failed", "error": str(e)}, status=400)
