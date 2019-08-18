from pathlib import Path

DATABASE_NAME = (Path(__file__).parent.parent.__str__() + "/paygo.db")
# sleep time in milliseconds for the sensor reads
SENSOR_SLEEP_SECONDS = 10  # TODO: change to 5 minutes after testing is done
DEVICE_ID = "1"
# price in USD per ml of water
PRICE_PER_ML = 0.02
# the milliliters represented by each rising edge of the flowmeter
ML_PER_PULSE = 2.2
# how many milliliters before we write to the db
FLOWMETER_THRESHOLD = 100
FLOWMETER_UNITS = "milliliters"
# total seconds in an hour
SECONDS_IN_HOUR = 3600

# PINOUT
FLOWMETER_PIN = "GPIO26"
RELAY_PIN = "GPIO20"
ORP_PIN = "GPIO16"

# retrieve the latest credit balance from the database
GET_BALANCE_QUERY = "SELECT CreditBalance FROM CreditAuditLog ORDER BY Timestamp DESC LIMIT 1"
INSERT_CREDIT_LOG_SQL = "INSERT INTO CreditAuditLog (CreditID, DeviceID, Timestamp, CreditBalance) values((?), (?), " \
                        "(?), (?))"

# how often the UI refreshes itself (in seconds)
UI_UPDATE_RATE = 5

# decimal places to round to in the UI
DIGITS_TO_ROUND = 3

ERROR_CODE = -9999

# these are for the ORP Sensor (DF Robot's SEN0165). They come from the arduino sample code at
# https://wiki.dfrobot.com/Analog_ORP_Meter_SKU_SEN0165_
ORP_SOURCE_MV = 5000
ORP_COEFFICIENT_A = 30
ORP_COEFFICIENT_B = 75
