import hashlib
import hmac
import requests
import json

from flask import request

from base64 import b64encode
from time import time
from uuid import uuid4

from errors import ProvisioningError
from secrets import yealink

# URLS & API credentials
BASE_URL = "https://api-dm.yealink.com:8443/"
API_KEY = yealink.get("api_key", "key")
API_SECRET = yealink.get("api_secret", "secret")


def provision(mac):
    payload = request.get_json()
    mac = mac.replace("-", "").lower()
    url = payload.get("url")

    req = None
    device_id = check_exists(mac)
    if device_id:
        req = device_edit(device_id, url)
    else:
        req = device_add(mac, url)

    if req is not None:
        raise ProvisioningError("unknown_response_from_provider", 500)


def check_exists(mac):
    endpoint = "api/open/v1/device/list"
    payload = {"key": mac}
    headers = sign_post(endpoint, payload)
    r = requests.post(BASE_URL + endpoint, headers=headers, json=payload)

    resp = r.json()

    data = resp.get("data").get("data")
    for phone in data:
        if phone.get("mac") == mac:
            return phone.get("id")
    return None


def device_edit(id, url):
    endpoint = "api/open/v1/device/edit"
    payload = {"id": id, "uniqueServerUrl": url}
    headers = sign_post(endpoint, payload)
    r = requests.post(BASE_URL + endpoint, headers=headers, json=payload)

    resp = r.json()
    error = resp.get("error")
    if error:
        return True


def device_add(mac, url):
    endpoint = "api/open/v1/device/add"
    payload = {"macs": [mac], "uniqueServerUrl": url}
    headers = sign_post(endpoint, payload)
    r = requests.post(BASE_URL + endpoint, headers=headers, json=payload)

    resp = r.json()
    error = resp.get("error")
    if error:
        return True


def sign_post(endpoint, payload):
    # md5 of the string value of the payload
    payload_str = json.dumps(payload, indent=None)
    payload_md5 = hashlib.md5(payload_str.encode()).digest()

    # headers text
    content_md5 = b64encode(payload_md5).decode()
    x_ca_key = API_KEY
    x_ca_nonce = str(uuid4())
    x_ca_timestamp = str(int(time() * 1000))

    # create the awkward digest
    def b_signature():
        stringToSign = (
            f"POST\n"
            f"Content-MD5:{ content_md5 }\n"
            f"X-Ca-Key:{ x_ca_key }\n"
            f"X-Ca-Nonce:{ x_ca_nonce }\n"
            f"X-Ca-Timestamp:{ x_ca_timestamp }\n"
            f"{ endpoint }"
        )
        auth = hmac.new(API_SECRET.encode(), stringToSign.encode(), hashlib.sha256)
        return auth.digest()

    x_ca_signature = b64encode(b_signature()).decode()

    headers = {
        "Content-MD5": content_md5,
        "X-Ca-Key": x_ca_key,
        "X-Ca-Nonce": x_ca_nonce,
        "X-Ca-Timestamp": x_ca_timestamp,
        "X-Ca-Signature": x_ca_signature,
    }
    return headers
