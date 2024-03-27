from sanic import Sanic, response
from dbmanage import Database
import urls

app = Sanic("elecbillApp")
db = Database(host="127.0.0.1",
              port=3306,
              user="root",
              password="22654298",
              db="elecbill")


@app.get("initelecbill/v1/<id>")
async def init_elecbill(request, id):
    pass


@app.get("elecbill/v1/<id>")
async def get_elecbill(request, id):
    pass


@app.put("elecbill/v1/<id>")
async def update_elecbill(request, id):
    pass


@app.delete("elecbill/v1/<id>")
async def delete_elecbill(request, id):
    pass


@app.post("data/v1")
async def post_data(request):
    pass


@app.get("data/v1/<id>")
async def get_data(request, id):
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010)
