import json
import os
from dataclasses import dataclass

from Crypto.PublicKey import RSA
from flask import Flask, Response, request

app = Flask(__name__)


@dataclass
class Actor:
    ap_id: str
    name: str
    domain: str
    private_key: str
    public_key: str

    def get_actor(self):
        return {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": self.ap_id,
            "preferredUsername": actor.name,
            "publicKey": {
                "id": f"{actor.ap_id}#main-key",
                "owner": actor.ap_id,
                "publicKeyPem": actor.public_key,
            },
            "type": "Person",
        }


def init_actor():
    user = os.getenv("USER")
    domain = os.getenv("DOMAIN")
    ap_id = f"https://{domain}/user/{user}"

    new_key = RSA.generate(2048)
    private_key = new_key.exportKey("PEM").decode("utf-8")
    public_key = new_key.publickey().exportKey("PEM").decode("utf-8")

    return Actor(
        ap_id=ap_id,
        name=user,
        domain=domain,
        private_key=private_key,
        public_key=public_key,
    )


actor = init_actor()


@app.route("/", methods=["GET"])
def hello_world():
    return "Hello World!"


@app.route("/.well-known/webfinger", methods=["GET"])
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
                "href": actor.ap_id,
                "rel": "self",
                "type": "application/activity+json",
            }
        ],
    }
    return Response(
        json.dumps(resp), status=200, content_type="application/jrd+json"
    )


@app.route("/user/<string:user>", methods=["GET"])
def get_actor(user):
    if user != actor.name:
        return Response(
            "", status=404, content_type="application/jrd+json; charset=utf-8"
        )

    resp = actor.get_actor()
    return Response(
        json.dumps(resp),
        status=200,
        content_type="application/jrd+json; charset=utf-8",
    )


if __name__ == "__main__":
    app.run()
