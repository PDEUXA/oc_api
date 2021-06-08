"""
Services for interacting with api.OC and OC website
"""
import re
from typing import Tuple, Union

import requests

from app.core.db import mongodb


async def login_oc(mail, pwd) -> dict:
    """
    Log to OC website to get token and cookies
    :param mail: str
    :param pwd: str
    :return: dict
    """
    req = requests.get('https://openclassrooms.com/fr/login_ajax')

    cookies = {"PHPSESSID": req.cookies['PHPSESSID']}
    state = req.json()['csrf']
    payload = {"_username": mail,
               '_password': pwd,
               'state': req.json()['csrf']}
    headers = {'x-requested-with': 'XMLHttpRequest'}
    req = requests.post("https://openclassrooms.com/login_check",
                        headers=headers,
                        cookies=cookies,
                        data=payload)
    if req.status_code != 200:
        raise RuntimeError(f'{req.content} returned {req.status_code}')
    await mongodb.save_cookies({"PHPSESSID": req.cookies['PHPSESSID'], "csrf_token": state})
    return {"state": True, "token": req.cookies['access_token']}


def update_session_api(user_id, range_min, range_max,
                       authorization, return_range=False) -> Union[dict, Tuple]:
    """
    Find all session in the range
    :param user_id:
    :param authorization:
    :param return_range:
    :param range_min: int
    :param range_max:  int
    :return: list of session, nb of session from parameter  Content Range
    """
    url = 'https://api.openclassrooms.com/users/'
    suffix = str(
        user_id) + '/sessions?actor=expert&life-cycle-status=canceled,' \
                   'completed,late canceled,marked student as absent'
    headers = {'Authorization': authorization,
               'Content-Type': 'application/json',
               'Range': 'items=' + str(range_min) + "-" + str(range_max),
               'Connection': 'keep-alive',
               'X-Requested-With': 'XMLHttpRequest'}
    req = requests.get(url + suffix, headers=headers)
    if req.status_code == 206:
        if return_range:
            return req.json(), int(req.headers['Content-Range'].split('/')[-1])
        return req.json()


def get_student_type(student_id, authorization, cookie) -> dict:
    """
    Get student type
    :param student_id: int
    :param authorization: str to interact with api oc
    :param cookie: str to interact with oc website
    :return: dict
    """
    rx_student_status = re.compile(r'<div class="mentorshipStudent__details oc-typography-body1"><p>([^<]+)</p>')

    url = 'https://openclassrooms.com/fr/mentorship/students/' + str(student_id) + '/dashboard'
    req = requests.get(url, cookies={"PHPSESSID": cookie})
    if req.status_code != 200:
        raise RuntimeError(f'{req.url} returned {req.status_code}')

    html = req.text.replace('\n', '')
    match_status = rx_student_status.search(html)
    if match_status is not None:
        status = {"status": match_status.group(1).strip()}
    else:
        status = {"status": "Ext"}

    url = 'https://api.openclassrooms.com/users/'
    suffix = str(student_id)
    headers = {'Authorization': authorization,
               'Content-Type': 'application/json',
               'Connection': 'keep-alive',
               'X-Requested-With': 'XMLHttpRequest'}
    req = requests.get(url + suffix, headers=headers)
    if req.status_code == 200:
        return {**req.json(), **status}


def schedule_meeting():
    pass
