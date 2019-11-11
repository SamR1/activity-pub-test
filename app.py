import base64
import json
import os
from dataclasses import dataclass
from datetime import datetime

import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from flask import Flask, Response, jsonify, request

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
            "inbox": f"https://{actor.domain}/inbox",
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


@app.route("/inbox", methods=["GET"])
def inbox():
    return "Success"


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
        json.dumps(resp), status=200, content_type='application/jrd+json'
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
        content_type='application/jrd+json; charset=utf-8',
    )


@app.route("/note", methods=["POST"])
def post_note():
    data = request.get_json()
    message = (
        data.get("message") if data else "<p>Trying to post a message!</p>"
    )
    host = data.get("host") if data else "mastodon.social"
    toot = data.get("toot") if data else "@Gargron/100254678717223630"
    toot_url = f"https://{host}/{toot}"

    now = datetime.utcnow()
    formatted_now = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    activity = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"https://{actor.domain}/create-test-note",
        "type": "Create",
        "actor": actor.ap_id,
        "object": {
            "id": f"https://{actor.domain}/note-message",
            "type": "Note",
            "published": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "attributedTo": actor.ap_id,
            "inReplyTo": toot_url,
            "content": message,
            "to": "https://www.w3.org/ns/activitystreams#Public",
        },
    }

    signed_string = (
        f"(request-target): post /inbox\nhost: {host}\ndate: {formatted_now}"
    )
    key = RSA.import_key(actor.private_key)
    key_signer = pkcs1_15.new(key)
    encoded_string = signed_string.encode("utf-8")
    h = SHA256.new(encoded_string)
    signature = base64.b64encode(key_signer.sign(h))
    header = (
        f'keyId="{actor.ap_id}",headers="(request-target) host date",'
        f'signature="' + signature.decode() + '"'
    )

    resp = requests.post(
        f"https://{host}/inbox",
        data=json.dumps(activity),
        headers={
            "Host": host,
            "Date": formatted_now,
            "Signature": header,
            "Content-Type": "application/ld+json",
        },
    )
    if resp.status_code >= 400:
        print(resp.text)
        response = {"status": "error"}
    else:
        response = {"status": "created"}
    code = resp.status_code

    return jsonify(response), code


if __name__ == "__main__":
    app.run()
