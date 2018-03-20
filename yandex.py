#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import settings
import json
url = "https://money.yandex.ru/to/410014484849976"

querystring = {"rows":"50","operation":"IN"}

headers = {
    'accept': "application/json",
    'authorization': "Bearer {}".format(settings.qiwi_token),
    'cache-control': "no-cache",
    }

def get_history(**kwargs):

    response = requests.request("GET", url, headers=headers, params=kwargs)
    if response.status_code == 200:

        return json.loads(response.text)
    else:
        return False

