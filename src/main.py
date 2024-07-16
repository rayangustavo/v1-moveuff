from os import environ
import logging
import requests
import json

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

def hex2str(hex):
    return bytes.fromhex(hex[2:]).decode("utf-8")

def str2hex(str):
    return "0x" + str.encode("utf-8").hex()

def add_notice(notice):
    try:
        notice = str2hex(notice)
        logger.info("Adding notice")
        response = requests.post(rollup_server + "/notice", json={"payload": notice})
        logger.info(f"Received notice status {response.status_code} body {response.content}")

    except Exception:
        logger.error("Error creating notice.")

    return

def handle_advance(data):
    logger.info(f"Received advance request data {data}")

    try:
        payload = json.loads(hex2str(data['payload']))
        logger.info(f"Initial Payload: {payload}")

        id_travel = payload["id_travel"]
        id_bike = payload["id_bike"]
        travelled_distance = payload["travelled_distance"]
        source_terminal = payload["source_terminal"]
        destination_terminal = payload["destination_terminal"]
        source_timestamp = payload["source_timestamp"]
        destination_timestamp = payload["destination_timestamp"]

    except Exception as err:
        logger.error(f"ERROR: {err}")

    return "accept"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        data = rollup_request["data"]
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
