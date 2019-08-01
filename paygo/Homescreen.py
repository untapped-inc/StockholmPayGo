import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Label
from kivy.uix.floatlayout import FloatLayout


# return balance in US Dollars
def get_balance():
    #     TODO: fetch the balance from Nick's API endpoints
    return 500


# returns the rate per Liter (should this come from the API?)
def get_rate():
    return 0.02


def get_flow_per_hour():
    # TODO: pull this from the database
    return 5


def get_volume_in_last_24_hours():
    return 514


def get_orp():
    #     TODO: pull the last orp from the database
    return 550


def get_tds():
    #     TODO: same as orp
    return 100


def get_flowmeter():
    #     TODO: figure out how to do this? Last MV reading? Last Time of Square Wave Change?
    return 100


class HomescreenApp(App):
    def build(self):
        dashboard_object = FloatLayout()
        # pull rate and consumption into separate variables for later use
        rate = get_rate()
        volume_last_24_hours = get_volume_in_last_24_hours()

        # populate the data in the dashboard
        dashboard_object.ids.credit_balance_text.text = "$" + get_balance().__str__() + " (USD)"
        dashboard_object.ids.rate_text.text = "$" + rate.__str__()
        dashboard_object.ids.average_flow_text.text = get_flow_per_hour().__str__() + " Liters per Minute"
        dashboard_object.ids.volume_24_text.text = volume_last_24_hours.__str__() + " Liters"
        dashboard_object.ids.balance_24_hours.text = "$" + (volume_last_24_hours * rate).__str__()
        dashboard_object.ids.orp_text.text = get_orp().__str__() + " mv"
        dashboard_object.ids.tds_text.text = get_tds().__str__() + " mv"
        dashboard_object.ids.flowmeter_text.text = get_flowmeter().__str__()

        return dashboard_object
