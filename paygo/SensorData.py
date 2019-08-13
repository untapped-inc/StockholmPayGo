import sqlite3
import time
import threading
import uuid
from gpiozero import DigitalInputDevice, DigitalOutputDevice

from paygo import Constants
from paygo.Constants import DATABASE_NAME, ML_PER_PULSE, FLOWMETER_THRESHOLD, DEVICE_ID, \
    FLOWMETER_UNITS, CREDITS_PER_ML, GET_BALANCE_QUERY, RELAY_PIN, SENSOR_SLEEP_SECONDS, INSERT_CREDIT_LOG_SQL

# global variable temporarily store the ml passing through the flowmeter until they can be written to the database
flowmeter_milliliters_cache = 0.0
# global variable to stores the user's credits between reads from the database
credit_balance_cache = 0.0


class SensorData(object):
    @classmethod
    def read_all_sensors(cls):
        set_flowmeter_callback()
        continue_looping = True
        # connect to the database
        conn = sqlite3.connect(DATABASE_NAME)
        # a cursor is needed to write to the db
        cur = conn.cursor()

        global credit_balance_cache
        # read the latest balance from the database to start the credit balance cache
        for balance in cur.execute(GET_BALANCE_QUERY):
            credit_balance_cache = balance[0]  # (there's only one, at most)
        # turn on the circuit if the balance is used
        if credit_balance_cache > 0.0:
            print("trying to turn on")  # TODO: remove this print
            relay_module = DigitalOutputDevice(RELAY_PIN, active_high=False, initial_value=False,
                                               pin_factory=None)
            relay_module.on()

        # loop until told to stop - read from the ORP, TDS, and write to the db along the way
        while continue_looping:
            print("looping")
            orp_mv = read_from_orp()
            # insert into ORP
            cur.execute("""INSERT INTO ORP (ReadingID, Millivolts, Timestamp, DeviceID,
                IsSynced) values((?), (?), (?), (?), 0) """, (uuid.uuid4().__str__(), orp_mv, int(time.time()),
                                                              Constants.DEVICE_ID))
            conn.commit()
            # sleep for a few minutes
            time.sleep(SENSOR_SLEEP_SECONDS)

def read_from_orp():
    # if on the pi, return an actual value, if testing, return some dummy data
    if Constants.IS_DEBUG:
        return 9999
    else:
        # TODO: pull information from ORP
        return 0


def set_flowmeter_callback():
    if Constants.IS_DEBUG:
        return
    else:
        # start new thread for flowmeter
        flowmeter_thread = threading.Thread(target=flowmeter_manager)
        flowmeter_thread.start()


# this sets a callback to listen to the flowmeter, then ends in an infinite loop - this is to allow the thread to
# work solely on listening for the flowmeter
def flowmeter_manager():
    # an object to interface with the flowmeter
    flowmeter_sensor = DigitalInputDevice(Constants.FLOWMETER_PIN)
    # setup callbacks to detect the rising edges (
    # https://gpiozero.readthedocs.io/en/stable/migrating_from_rpigpio.html)
    flowmeter_sensor.when_activated = count_flowmeter_pulse
    while True:
        # create an infinite loop so that the flowmeter listerner never dies
        pass


# function that is called every time a rising edge is detected on the flowmeter sensor
def count_flowmeter_pulse():
    print("flowmeter pulse!")  # todo: remove this
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
    # increment the water counter until the threshold is breached
    # this is not done every time a pulse is detected to cut down on the database writes produced by this code
    global flowmeter_milliliters_cache
    flowmeter_milliliters_cache += ML_PER_PULSE

    # track the user's credit balance as water is consumed
    global credit_balance_cache
    credit_balance_cache = calculate_balance(credit_balance_cache)

    # cut off the relay after a balance of zero is reached
    if credit_balance_cache <= 0.0:
        disconnect_relay()

    # check for threshold breach
    if flowmeter_milliliters_cache >= FLOWMETER_THRESHOLD:
        # write another pulse to the database
        cur.execute("INSERT INTO WaterLog (FlowmeterReadingID, DeviceID, Timestamp, Value, Units) values((?), (?), "
                    "(?), (?), (?))", (uuid.uuid4().__str__(), DEVICE_ID, int(time.time()), flowmeter_milliliters_cache,
                                       FLOWMETER_UNITS))
        cur.execute(INSERT_CREDIT_LOG_SQL, (uuid.uuid4().__str__(), DEVICE_ID, int(time.time()),
                                            credit_balance_cache))
        # commit both transactions
        conn.commit()


# function that takes in user's credit balance and subtracts the milliliters consumed in the last pulse
def calculate_balance(credit_balance):
    return credit_balance - (ML_PER_PULSE * CREDITS_PER_ML)


# turns off the relay (which turns off the motor/solenoid)
def disconnect_relay():
    # this object represents the relay board. Notice that active_high is false! This is because the relay should be
    # LOW to close the circuit and turn on the motor!
    relay_module = DigitalOutputDevice(RELAY_PIN, active_high=False, initial_value=False,
                                       pin_factory=None)
    # turns the relay off
    relay_module.off()
