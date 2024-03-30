import configparser
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, "config.ini"))

db = {
    'user': config.get("database", "username"),
    'password': config.get("database", "password"),
    'name': config.get("database", "database"),
    'port': int(config.get("database", "port")),
    'host': config.get("database", "host")
}

server = {
    'host': config.get("server", "host"),
    'port': int(config.get("server", "port"))
}
