import sqlite3
import threading
import time

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from datetime import datetime

from paygo import Constants
from paygo.Constants import DATABASE_NAME, GET_BALANCE_QUERY, SECONDS_IN_HOUR, UI_UPDATE_RATE


# placeholder object for the add credits screen
class AddScreen(Screen):
    pass


# placeholder object for the home screen that's defined in homescreen.kv
class HomeScreen(Screen):
    pass


class ConfirmPurchase(Screen):
    pass


# placeholder object for the KivyManager that's defined in the homescreen.kv
class KivyManager(ScreenManager):
    pass


class HomescreenApp(App):
    dashboard_object = None
    cur = None
    # dashboard_object = None
    last_upsync_time = None
    last_downsync_time = None

    def build(self):
        self.dashboard_object = KivyManager()
        print("build")
        # manage the update process in another thread - the Clock scheduler in kivy always locks up my app
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
                print(self.dashboard_object)  # todo: remove
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

    # return balance in US Dollars
    def get_balance(self):
        new_conn = sqlite3.connect(DATABASE_NAME)
        # a cursor is needed to talk to the db
        new_cursor = new_conn.cursor()

        balance = 0.0
        # get the latest balance out of the database
        balance_query = new_cursor.execute(GET_BALANCE_QUERY)

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

    def add_credit_button_click(self, button_text):
        # should only be one active child
        text_display = self.dashboard_object.children[0].ids.add_amount.text
        # remove the dollar sign (the first character)
        text_display = text_display[1:]
        if button_text == '<':
            if len(text_display) > 1:
                # remove the last character
                text_display = text_display[:-1]
            else:
                text_display = "0"
            self.update_new_balance(text_display)
        else:
            # ignore multiple decimal points
            if not (text_display.count('.') > 0 and button_text == '.'):
                text_display += button_text
                # todo: check to make sure that the display text doesn't consist of only a decimal point
                self.update_new_balance(text_display)
        # make sure that we don't have a weird number with a 0 in the front
        if len(text_display) > 1 and text_display[0] == '0' and text_display[1] != '.':
            text_display = text_display[1:]

        # reassign
        self.dashboard_object.children[0].ids.add_amount.text = "$" + text_display

    # helper function to update the new balance on the add credits menu
    def update_new_balance(self, text_display):
        new_money = float(text_display)
        old_money = float(self.get_balance())
        try:
            self.dashboard_object.children[0].ids.new_balance_text.text = "$" + (new_money + old_money).__str__()
        except Exception:
            print("This only is to be used within the add credits screen")

    def confirm_transaction(self, new_credit):
        print("confirm")
        # setup the message
        try:
            # confirmation screen is the 3rd in the array - probably need to find a better way to do this in the future
            self.root.screens[2].ids.confirmation_text.text = "You are about to purchase " + new_credit + \
                                                              " of water" \
                                                              " credit! Press Confirm to continue. Otherwise, " \
                                                              "press Cancel. "
        except Exception:
            print("Error confirming transaction")
        # move to the next screen
        self.root.current = 'confirm_screen'
