import json
import os
from dataclasses import dataclass

from Crypto.PublicKey import RSA
from flask import Flask, Response, request

app = Flask(__name__)


@dataclass
class Actor:
    name: str
    domain: str
    private_key: str
    public_key: str


def init_actor():
    user = os.getenv("USER")
    domain = os.getenv("DOMAIN")

    new_key = RSA.generate(2048)
    private_key = new_key.exportKey("PEM").decode("utf-8")
    public_key = new_key.publickey().exportKey("PEM").decode("utf-8")

    return Actor(
        name=user,
        domain=domain,
        private_key=private_key,
        public_key=public_key,
    )


actor = init_actor()


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/.well-known/webfinger")
def webfinger():
    resource = request.args.get("resource")
    if not resource or not resource.startswith("acct:"):
        return Response(
            "", status=400, content_type="application/jrd+json; charset=utf-8"
        )

    account = resource.replace("acct:", "")
    name = account.split("@")[0]
    domain = account.split("@")[1]

    if not name or name != actor.name or not domain or domain != actor.domain:
        return Response(
            "", status=404, content_type="application/jrd+json; charset=utf-8"
        )
    resp = {
        "subject": f"acct:{actor.name}@{actor.domain}",
        "links": [
            {
                "href": f"https://{actor.domain}/user/{actor.name}",
                "rel": "self",
                "type": "application/activity+json",
            }
        ],
    }
    return Response(
        json.dumps(resp), status=200, content_type="application/jrd+json"
    )


if __name__ == "__main__":
    app.run()
