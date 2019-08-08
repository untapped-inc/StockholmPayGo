import sqlite3
import threading
import time

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.button import Label
from kivy.uix.floatlayout import FloatLayout
from datetime import datetime

from paygo import Constants
from paygo.Constants import DATABASE_NAME, GET_BALANCE_QUERY, SECONDS_IN_HOUR, UI_UPDATE_RATE


class HomescreenApp(App):
    dashboard_object = None
    cur = None
    # dashboard_object = None
    last_upsync_time = None
    last_downsync_time = None

    def build(self):
        self.dashboard_object = FloatLayout()
        self.dashboard_object.ids.rate_text.text = "hello world"

        update_thread = threading.Thread(target=self.refresh_ui)

        update_thread.start()

        return self.dashboard_object

    def refresh_ui(self):
        # open a db connection for later querying
        conn = sqlite3.connect(DATABASE_NAME)
        # a cursor is needed to talk to the db
        self.cur = conn.cursor()
        while True:
            rate = self.get_rate()
            volume_last_24_hours = self.get_volume_in_last_24_hours()
            if self.dashboard_object is not None:
                print("2")
                self.dashboard_object.ids.rate_text.text = rate.__str__()
                self.dashboard_object.ids.credit_balance_text.text = "$" + self.get_balance() + " (USD)"
                self.dashboard_object.ids.rate_text.text = "$" + rate.__str__()
                self.dashboard_object.ids.average_flow_text.text = self.get_flow_per_hour().__str__() + " Liters per Minute"
                self.dashboard_object.ids.volume_24_text.text = volume_last_24_hours.__str__() + " Liters"
                self.dashboard_object.ids.balance_24_hours.text = "$" + (volume_last_24_hours * rate).__str__()
                self.dashboard_object.ids.orp_text.text = self.get_orp().__str__() + " mv"
                self.dashboard_object.ids.tds_text.text = self.get_tds().__str__() + " mv"
                # convert unix timestamps to human-readable times for this
                self.dashboard_object.ids.flowmeter_text.text = datetime.fromtimestamp(self.get_flowmeter()).__str__()
                if self.last_downsync_time is not None:
                    self.dashboard_object.ids.downsync_text.text = datetime.fromtimestamp(
                        self.last_downsync_time).__str__()
                if self.last_upsync_time is not None:
                    self.dashboard_object.ids.upsync_text.text = datetime.fromtimestamp(self.last_upsync_time).__str__()
            time.sleep(UI_UPDATE_RATE)

    # def refresh_ui(self):
    #     # open a db connection for later querying
    #     conn = sqlite3.connect(DATABASE_NAME)
    #     # a cursor is needed to talk to the db
    #     self.cur = conn.cursor()
    #     print("refreshing")
    #     # pull rate and consumption into separate variables for later use
    #     rate = self.get_rate()
    #     volume_last_24_hours = self.get_volume_in_last_24_hours()
    #
    #     if self.dashboard_object is not None:
    #         # self.dashboard_object.ids.credit_balance_text.text = "test"
    #         # "$" + self.get_balance() + " (USD)"
    #         self.dashboard_object.ids.rate_text.text = "$" + rate.__str__()
    #         self.dashboard_object.ids.average_flow_text.text = self.get_flow_per_hour().__str__() + " Liters per Minute"
    #         self.dashboard_object.ids.volume_24_text.text = volume_last_24_hours.__str__() + " Liters"
    #         self.dashboard_object.ids.balance_24_hours.text = "$" + (volume_last_24_hours * rate).__str__()
    #         self.dashboard_object.ids.orp_text.text = self.get_orp().__str__() + " mv"
    #         self.dashboard_object.ids.tds_text.text = self.get_tds().__str__() + " mv"
    #         # convert unix timestamps to human-readable times for this
    #         self.dashboard_object.ids.flowmeter_text.text = datetime.fromtimestamp(self.get_flowmeter()).__str__()
    #         if self.last_downsync_time is not None:
    #             self.dashboard_object.ids.downsync_text.text = datetime.fromtimestamp(
    #                 self.last_downsync_time).__str__()
    #         if self.last_upsync_time is not None:
    #             self.dashboard_object.ids.upsync_text.text = datetime.fromtimestamp(self.last_upsync_time).__str__()
    #
    # return balance in US Dollars
    def get_balance(self):
        balance = 0.0
        # get the latest balance out of the database
        balance_query = self.cur.execute(GET_BALANCE_QUERY)

        for data in balance_query:
            balance = data[0]

        return str(balance)

    # returns the rate per Liter (should this come from the API?)
    def get_rate(self):
        # check the database to see if the rate has changed
        rate_query = self.cur.execute("SELECT PricePerML, LastUpSyncTime, LastDownSyncTime UpSync FROM Device LIMIT 1")

        for data in rate_query:
            # this should be stored globally
            if data[0] is not None:
                Constants.CREDITS_PER_ML = data[0]
            if data[1] is not None:
                self.last_downsync_time = data[1]
            if data[2] is not None:
                self.last_upsync_time = data[2]

        print("rate")

        return Constants.CREDITS_PER_ML

    # returns the flow rate per minute for the past hour
    def get_flow_per_hour(self):
        flow = 0.0
        current_time = int(time.time())
        start_time = current_time - (1 * SECONDS_IN_HOUR)
        flow_query = self.cur.execute("SELECT SUM(VALUE) FROM WaterLog WHERE TIMESTAMP BETWEEN (?) AND (?)",
                                      (start_time, current_time))
        for data in flow_query:
            if data[0] is not None:
                flow = data[0]

        # divide the liters in the past hour by the total minutes in an hour
        return flow / 60.0

    def get_volume_in_last_24_hours(self):
        volume = 0
        current_time = int(time.time())
        start_time = current_time - (24 * SECONDS_IN_HOUR)
        volume_query = self.cur.execute("SELECT SUM(VALUE) FROM WaterLog WHERE TIMESTAMP BETWEEN (?) AND (?)",
                                        (start_time, current_time))
        for data in volume_query:
            if data[0] is not None:
                volume = data[0]

        return volume

    def get_orp(self):
        orp = 0.0
        #     pull the last orp from the database
        orp_query = self.cur.execute("SELECT Millivolts FROM ORP ORDER BY Timestamp DESC LIMIT 1")
        for data in orp_query:
            orp = data[0]
        return orp

    def get_tds(self):
        tds = 0.0
        #    same as orp
        tds_query = self.cur.execute("SELECT Millivolts FROM TDS ORDER BY Timestamp DESC Limit 1")
        for data in tds_query:
            tds = data[0]
        return tds

    def get_flowmeter(self):
        timestamp = 0
        # pull the latest water log timestamp
        flowmeter_time_query = self.cur.execute("SELECT Timestamp FROM WaterLog ORDER BY Timestamp DESC Limit 1")
        for data in flowmeter_time_query:
            if data[0] is not None:
                timestamp = data[0]

        return timestamp
