import sqlite3
import logging

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

DB_PATH = "./"

def connect_db(db):
    db = DB_PATH + db
    try:
        con = sqlite3.connect(db)
        logger.info(f"Connection to database {db} established.")
        return con
    except sqlite3.Error as error:
        logger.error(error)

def create_tables(con):
    user_table = """ CREATE TABLE IF NOT EXISTS Users (
	            id_user INTEGER PRIMARY KEY AUTOINCREMENT, 
	            name VARCHAR(200),
	            address VARCHAR(42) NOT NULL
                ); """
    
    bike_table = """ CREATE TABLE IF NOT EXISTS Bikes (
                id_bike INTEGER PRIMARY KEY AUTOINCREMENT,
                serial_number VARCHAR(200)
                )"""

    parking_station_table = """ CREATE TABLE IF NOT EXISTS Parking_Stations (
                id_parking_station INTEGER PRIMARY KEY AUTOINCREMENT, 
                address VARCHAR(200)
                ); """
    
    trip_table = """ CREATE TABLE IF NOT EXISTS Trips (
                id_trip INTEGER PRIMARY KEY AUTOINCREMENT,
                id_source_parking_station INTEGER,
                id_destination_parking_station INTEGER,
                time INTEGER,
                distance REAL,
                CONSTRAINT fk_SourceParkingStation FOREIGN KEY (id_source_parking_station) REFERENCES Parking_Stations (id_parking_station),
                CONSTRAINT fk_DestinationParkingStation FOREIGN KEY (id_destination_parking_station) REFERENCES Parking_Stations (id_parking_station)
                ); """

    token_table = """ CREATE TABLE IF NOT EXISTS Tokens (
                id_token INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200),
                symbol VARCHAR(5),
                address VARCHAR(200) NOT NULL
                ); """

    bike_x_parking_station_table = """ CREATE TABLE IF NOT EXISTS Bike_ParkingStation (
                id_bike INT NOT NULL, 
                id_parking_station INT NOT NULL,
                entry_time REAL,
                CONSTRAINT fk_Bike_BxTe FOREIGN KEY (id_bike) REFERENCES Bikes (id_bike),
                CONSTRAINT fk_Terminal_BxTe FOREIGN KEY (id_parking_station) REFERENCES Parking_Stations (id_parking_station)
                ); """
    
    bike_x_trip_table = """ CREATE TABLE IF NOT EXISTS Bike_Trip (
                id_bike INT NOT NULL, 
                id_trip INT NOT NULL,
                CONSTRAINT fk_Bike_BxTr FOREIGN KEY (id_bike) REFERENCES Bike (id_bike),
                CONSTRAINT fk_Trip_BxTr FOREIGN KEY (id_trip) REFERENCES Terminal (id_trip)
                ); """

    user_x_token_table = """ CREATE TABLE IF NOT EXISTS User_Token (
                id_user INT NOT NULL, 
                id_token INT NOT NULL,
                balance INT,
                CONSTRAINT fk_User_UxT FOREIGN KEY (id_user) REFERENCES Users (id_user),
                CONSTRAINT fk_Token_UxT FOREIGN KEY (id_token) REFERENCES Tokens (id_token)
                ); """

    trip_x_token_table = """ CREATE TABLE IF NOT EXISTS Trip_Token (
                id_trip INT NOT NULL, 
                id_token INT NOT NULL,
                generated_tokens INT,
                CONSTRAINT fk_Trip_TrxT FOREIGN KEY (id_trip) REFERENCES Trips (id_trip),
                CONSTRAINT fk_Token_TrxT FOREIGN KEY (id_token) REFERENCES Tokens (id_token)
                ); """
    
    user_x_trip_table = """ CREATE TABLE IF NOT EXISTS User_Trip (
                id_user INT NOT NULL, 
                id_trip INT NOT NULL,
                generated_tokens INT,
                CONSTRAINT fk_User_UxTr FOREIGN KEY (id_user) REFERENCES Users (id_user),
                CONSTRAINT fk_Trip_UxTr FOREIGN KEY (id_trip) REFERENCES Trip (id_trip)
                ); """

    tables = [user_table, bike_table, parking_station_table, trip_table, token_table, bike_x_parking_station_table, bike_x_trip_table, user_x_token_table, trip_x_token_table, user_x_trip_table]
    try:
        cur = con.cursor()
        for t in tables:
            cur.execute(t)
        logger.info("All tables have been created.")
    except sqlite3.Error as error:
        logger.error(error)

def init_bikes_table(con):
    bikes = [("R42A3Y",), ("J56O7S",), ("D89A0N",)]
    try:
        cur = con.cursor()
        cur.executemany("INSERT INTO Bikes (serial_number) VALUES (?)", bikes)
        logger.info("Table Inicialized: Bikes.")
        con.commit()
    except sqlite3.Error as error:
        logger.error(error)

def init_tokens_table(con):
    tokens = [("MoveUFF", "MUFF", "0x59b670e9fa9d0a427751af201d676719a970857b")]
    # tokens = [("MoveUFF", "MUFF", "0x4ed7c70F96B99c776995fB64377f0d4aB3B0e1C1")]
    try:
        cur = con.cursor()
        cur.executemany("INSERT INTO Tokens (name, symbol, address) VALUES (?, ?, ?)", tokens)
        logger.info("Table Inicialized: Tokens.")
        con.commit()
    except sqlite3.Error as error:
        logger.error(error)

def insert_trip(con, trip):
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO Trips (id_source_parking_station, id_destination_parking_station, time, distance) VALUES (?, ?, ?, ?)", trip)
        id_trip = cur.lastrowid
        logger.info(f"Inserted Trip: {trip} - ID: {id_trip}.")
        con.commit()
        return id_trip
    except sqlite3.Error as error:
        logger.error(error)

def insert_trip_x_token(con, generated_carbon_token, id_token, id_user, id_trip):
    try:
        cur = con.cursor()

        cur.execute("INSERT INTO Trip_Token (id_trip, id_token, generated_tokens) VALUES (?, ?, ?)", (id_trip, id_token, generated_carbon_token))
        logger.info(f"New Generated Tokens - TOKEN ID: {id_token}, TOKENS GENERATED: {generated_carbon_token}.")

        cur.execute("SELECT balance FROM User_Token WHERE id_user=? AND id_token=?", (id_user, id_token))
        selected_balance = cur.fetchone()
        if selected_balance != None:
            previous_balance = selected_balance[0]
            new_balance = previous_balance + generated_carbon_token
            cur.execute("UPDATE User_Token SET balance=? WHERE id_user=? AND id_token=?", (new_balance, id_user, id_token))
        else:
            new_balance = generated_carbon_token
            cur.execute("INSERT INTO User_Token (id_user, id_token, balance) VALUES (?, ?, ?)", (id_user, id_token, new_balance))
        logger.info(f"New User Balance -  USER ID: {id_user}, TOKEN ID: {id_token}, BALANCE: {new_balance}.")
        con.commit()
    except sqlite3.Error as error:
        logger.error(error)
    return

def insert_user_x_trip(con, id_user, id_trip, generated_tokens):
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO User_Trip (id_user, id_trip, generated_tokens) VALUES (?, ?, ?)", (id_user, id_trip, generated_tokens))
        logger.info(f"New User_Trip added - User: {id_user}, Trip: {id_trip}, Generated Tokens: {generated_tokens}")
        con.commit()
    except sqlite3.Error as error:
        logger.error(error)
    return

def update_user_tokens_from_user_address(con, user_address, token_address, amount):
    try:
        cur = con.cursor()
        cur.execute("SELECT id_user FROM Users WHERE address=?", (user_address,))
        id_user = cur.fetchone()[0]

        cur.execute("SELECT id_token FROM Tokens WHERE address=?", (token_address,))
        id_token = cur.fetchone()[0]
        
        cur.execute("SELECT balance FROM User_Token WHERE id_user=? AND id_token=?", (id_user, id_token))
        balance = cur.fetchone()
        if balance == None:
            balance = 0
        else:
            balance = balance[0]
        new_balance = balance + amount
        logger.info(f"NEW BALANCE: {new_balance}")
        cur.execute("UPDATE User_Token SET balance=? WHERE id_user=? AND id_token=?", (new_balance, id_user, id_token))
        logger.info(f"Updated Balance - User: {id_user}, Token: {id_token}, Previous Balance: {balance}, New Balance: {new_balance}")
        con.commit()
        return
    except sqlite3.Error as error:
        logger.error(error)
    return

def insert_bike_x_trip(con, id_bike, id_trip):
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO Bike_Trip (id_bike, id_trip) VALUES (?, ?)", (id_bike, id_trip))
        logger.info(f"New Bike_Trip added - Bike: {id_bike}, Trip: {id_trip}")
        con.commit()
    except sqlite3.Error as error:
        logger.error(error)
    return

def insert_bike_x_parking_station(con, id_bike, id_parking_station, entry_time):
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO Bike_Bike_ParkingStation (id_bike, id_parking_station, entry_time) VALUES (?, ?, ?)", (id_bike, id_parking_station, entry_time))
        logger.info(f"New Bike_ParkingStation added - Bike: {id_bike}, Parking Station: {id_parking_station}, Entry Time: {entry_time}")
        con.commit()
    except sqlite3.Error as error:
        logger.error(error)
    return

def update_bike_x_parking_station(con, id_bike, id_destination_parking_station, entry_time):
    try:
        cur = con.cursor()
        cur.execute("UPDATE Bike_ParkingStation SET id_parking_station=? AND entry_time=? WHERE id_bike=?", (id_destination_parking_station, entry_time, id_bike))
        logger.info(f"Updated Bike_ParkingStation - Bike: {id_bike}, Parking Station: {id_destination_parking_station}, Entry Time: {entry_time}")
        con.commit()
    except sqlite3.Error as error:
        logger.error(error)
    return

def insert_user(con, name, address, token_balance):
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO Users (name, address) VALUES (?, ?)", (name, address))
        id_user = cur.lastrowid
        logger.info(f"New User added - User {id_user}: ({name}, {address})")

        id_token = 1
        cur.execute("INSERT INTO User_Token (id_user, id_token, balance) VALUES (?, ?, ?)", (id_user, id_token, token_balance))
        logger.info(f"New User_Token added - User: {id_user}, Token: {id_token}, Balance: {token_balance}")
        con.commit()
    except sqlite3.Error as error:
        logger.error(error)
    return

def verify_if_user_exists_from_user_address(con, user_address):
    cur = con.cursor()
    cur.execute("SELECT * FROM Users WHERE address=?", (user_address,))
    selectedUser = cur.fetchone()
    if selectedUser == None:
        return False
    return True

def show_bikes(con):
    try:
        cur = con.cursor()
        res = cur.execute("SELECT * FROM Bikes")
        bikes = res.fetchall()
        return bikes
    except sqlite3.Error as error:
        logger.error(error)

con = connect_db("moveuff.db")
create_tables(con)
init_bikes_table(con)
init_tokens_table(con)
con.close()