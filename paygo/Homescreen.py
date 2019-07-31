import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Label
from kivy.uix.floatlayout import FloatLayout


# return balance in US Dollars
def get_balance():
    #     TODO: fetch the balance from Nick's API endpoints
    return 500


class HomescreenApp(App):
    def build(self):
        dashboardObject = FloatLayout()
        # dashboardObject.ids.home_scroll.ids.scroll_grid.ids.credit_balance_text.text = "testststs"
        # populate the data in the dashboard
        dashboardObject.ids.credit_balance_text.text = "$" + get_balance().__str__() + " (USD)"
        # dashboardObject.credit
        return dashboardObject
