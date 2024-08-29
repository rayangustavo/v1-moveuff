from os import environ
import logging
import requests
import json
import db_manager as dbm

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

def calculates_new_generated_tokens(travelled_distance):
    generated_carbon_token = int(travelled_distance/1000) + 1 
    return generated_carbon_token

def new_trip(con, id_user, id_bike, travelled_distance, source_parking_station, destination_parking_station, source_timestamp, destination_timestamp):
    trip_time = destination_timestamp - source_timestamp
    trip = (source_parking_station, destination_parking_station, trip_time, travelled_distance)
    id_trip = dbm.insert_trip(con, trip)

    id_token = 1
    generated_carbon_token = calculates_new_generated_tokens(travelled_distance)
    
    dbm.insert_trip_x_token(con, generated_carbon_token, id_token, id_user, id_trip)
    dbm.insert_user_x_trip(con, id_user, id_trip, generated_carbon_token)
    dbm.insert_bike_x_trip(con, id_bike, id_trip)
    dbm.update_bike_x_parking_station(con, id_bike, destination_parking_station, destination_timestamp)
    return

def receive_erc20_token(payload):
    try:
        logger.info("# Portal Payload #")
        erc20Address = "0x" + payload[4:44]
        msgSender = "0x" + payload[44:84]
        amount = int(payload[84:-26], 16)
        option = (payload[-26:], hex2str("0x" + payload[-26:]))

        logger.info(f"ERC-20: {erc20Address}")
        logger.info(f"Sender: {msgSender}")
        logger.info(f"Amount: {amount}")
        logger.info(f"Option: {option}")

        con = dbm.connect_db("moveuff.db")
        userExists = dbm.verify_if_user_exists_from_user_address(con, msgSender)
        if userExists:
            logger.info(f"User Exists: Updating Balance...")
            dbm.update_user_tokens_from_user_address(con, msgSender, erc20Address, amount)
        else:
            logger.info(f"User Not Exists: Inserting New User and Balance...")
            dbm.insert_user(con, "", msgSender, amount)
        con.close()

    except Exception as err:
        logger.error(f"ERROR: {err}")

def withdraw_tokens(payload):
    try:
        msgSender = "0x" + payload[44:84]
        amount = int(payload[84:-26], 16)
        voucher = f"transfer({msgSender}, {amount})"
        voucher = str2hex(voucher)
        logger.info("Adding voucher")
        response = requests.post(rollup_server + "/voucher", json={"payload": voucher})
        logger.info(f"Received voucher status {response.status_code} body {response.content}")
    except Exception:
        logger.error("Error creating voucher.")
    return

def handle_advance(data):
    logger.info(f"Received advance request data {data}")

    # ERC-20 Deposit (Portal Payload)
    if data["payload"].endswith(str2hex("erc20_deposit")[2:]):
        receive_erc20_token(data["payload"])
        # withdraw_tokens(data["payload"])
        return "accept"

    try:
        payload = json.loads(hex2str(data['payload']))
        logger.info(f"Initial Payload: {payload}")

        option = payload["option"]

        if option == "new_user":
            name = payload["name"]
            address = payload["address"]

            con = dbm.connect_db("moveuff.db")
            dbm.insert_user(con, name, address, 0)
            con.close()

        if option == "new_trip":
            id_user = payload["id_user"]
            id_bike = payload["id_bike"]
            travelled_distance = payload["travelled_distance"]
            source_parking_station = payload["source_parking_station"]
            destination_parking_station = payload["destination_parking_station"]
            source_timestamp = payload["source_timestamp"]
            destination_timestamp = payload["destination_timestamp"]

            con = dbm.connect_db("moveuff.db")
            new_trip(con, id_user, id_bike, travelled_distance, source_parking_station, destination_parking_station, source_timestamp, destination_timestamp)
            con.close()

    except Exception as err:
        logger.error(f"ERROR: {err}")

    return "accept"

def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    con = dbm.connect_db("moveuff.db")
    bikes = dbm.show_bikes(con)
    logger.info(f"BIKES: {bikes}")

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
