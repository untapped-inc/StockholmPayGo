import sqlite3
import time
import uuid

from paygo import Constants
from paygo.Constants import DATABASE_NAME, SENSOR_SLEEP_MS


class SensorData(object):
    @classmethod
    def read_all_sensors(cls):
        continue_looping = True
        # connect to the database
        conn = sqlite3.connect(DATABASE_NAME)
        # a cursor is needed to write to the db
        cur = conn.cursor()
        # loop until told to stop - read from the ORP, TDS, and write to the db along the way
        while continue_looping:
            # TODO: pull information from ORP and TDS
            orp_mv = 550
            # insert into ORP
            cur.execute("""INSERT INTO ORP (ReadingID, Millivolts, Timestamp, DeviceID,
                IsSynced) values((?), (?), (?), (?), 0) """, (uuid.uuid4().__str__(), orp_mv, int(time.time()),
                                                              Constants.DEVICE_ID))
            conn.commit()
            # sleep for a few minutes
            time.sleep(SENSOR_SLEEP_MS)
