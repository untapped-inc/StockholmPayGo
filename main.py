#!/usr/bin/env python3
import time
import sqlite3
import threading

from kivy.clock import Clock

from paygo import Communication, SensorData, Constants
from paygo.Constants import DATABASE_NAME
from paygo.Homescreen import HomescreenApp
from kivy.config import Config


def set_device_id():
    conn = sqlite3.connect(DATABASE_NAME)
    # a cursor is needed to write to the db
    cur = conn.cursor()
    # check to see if device id is already in existence or not
    device_query = "SELECT DeviceID FROM Device LIMIT 1"
    devices_exist = False
    # there should only ever be one result, at most
    for deviceID in cur.execute(device_query):
        Constants.DEVICE_ID = deviceID[0]
        devices_exist = True
    if devices_exist is False:
        # insert into the device table
        cur.execute("INSERT INTO Device (DeviceID, PricePerML) values((?),(?))", (Constants.DEVICE_ID.__str__(),
                                                                                  Constants.PRICE_PER_ML))
        conn.commit()


def ui_execution():
    homescreen_instance = HomescreenApp()
    homescreen_instance.run()


def main():
    # start as a full screen
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'window_state', 'maximized')
    Config.write()
    # set the device id if not already set (otherwise, retrieve it)
    set_device_id()

    # talk to the sensors and write to the DB
    sensor_thread = threading.Thread(target=SensorData.SensorData.read_all_sensors)

    # TODO: communication with the API
    comm_thread = threading.Thread(target=Communication.Communication.sync_with_server)

    sensor_thread.start()

    # object to manage the dashboard
    ui_thread = threading.Thread(target=ui_execution)

    ui_thread.start()

    # Get Demo
    #
    # # base path url for the paygo API endpoints
    # base = "http://pgw.semawater.org"
    # getPath = "/sema/water-ops/pgwc/1"
    # URL = base + getPath
    #
    # # http://pgw.semawater.org:80/sema/water-ops/pgwc/1
    #
    # r = requests.get(url=URL)
    # # extract the JSON
    # data = r.json()
    #
    # print(data)
    #
    # # POST Test
    #
    # postPath = "/sema/water-ops/pgwc"
    # postURL = base + postPath
    #
    # # request body example
    # requestBody = Communication.Communication.get_request_body(1563979540, 123, 1563979561, 456, 1, -1, -1, 1563979561)
    #
    # # Send the POST
    # postReply = requests.post(url=postURL, json=requestBody)
    #
    # print("Post Reply")
    # print(postReply.json())


main()
