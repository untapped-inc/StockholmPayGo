#!/usr/bin/env python3

import requests
from paygo import Communication
from paygo.Homescreen import HomescreenApp
from kivy.config import Config


def main():
    # start the user interface
    homescreen_instance = HomescreenApp()
    # if __name__ == "__main__":
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'window_state', 'maximized')
    Config.write()
    homescreen_instance.run()

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
