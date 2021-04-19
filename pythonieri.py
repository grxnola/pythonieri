import re
import json
from flask import Flask, request, Response
from urllib.parse import urlparse

from errors import ProvisioningError
import providers.yealink


app = Flask(__name__)

# validates
def validate(mac):
    def require(condition, error, status=400):
        if not condition:
            raise ProvisioningError(error, status)

    require(mac, "missing_mac_address")
    require(re.search("^([0-9a-fA-F]{2}-?){6}$", mac), "malformed_mac_address")

    url = request.get_json().get("url")
    require(url, "missing_url")

    parsed = urlparse(url)
    require(parsed, "malformed_url")
    require(parsed.scheme in ["http", "https", "ftp", "tftp"], "unsupported_url_scheme")

    return mac


@app.errorhandler(ProvisioningError)
def handle_provisioningerror(e):
    return Response(
        json.dumps({"error": e.error}), status=e.status, mimetype="application/json"
    )


@app.route("/providers/<provider>/<mac>", methods=["POST"])
def unsupported(provider, mac):
    raise ProvisioningError("provider_not_supported", 404)


@app.route("/providers/yealink/<string:mac>", methods=["POST"])
def yealink(mac):
    validate(mac)
    providers.yealink.provision(mac)

    return Response("{}", status=200, mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)
    exit()
