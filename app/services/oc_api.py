"""
Services for interacting with api.OC and OC website
"""
import re
from datetime import timedelta
from typing import Tuple, Union

import requests
from fastapi import HTTPException
from starlette import status

from app.core.db import mongodb
from app.schema.sessions import SessionScheduleInModel, SessionScheduleRequestModel


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(req.content))
    await mongodb.save_cookies({"PHPSESSID": req.cookies['PHPSESSID'], "access_token": req.cookies['access_token']})
    return {"state": True, "token": req.cookies['access_token']}


def delete_session_oc(session_id, cookie):
    url = "https://openclassrooms.com/api/mentorship-sessions/" + str(session_id) + "/cancel"

    headers = {"Content-Type": "application/json",
               'Connection': 'keep-alive',
               'X-Requested-With': 'XMLHttpRequest'}
    payload = "{\"late\": false, \"studentFacingNote\": null}"
    req = requests.post(url, cookies={"PHPSESSID": cookie}, headers=headers, data=payload)
    print(req.status_code, req.text)
    if req.status_code == 200:
        return req


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
                   'completed,late canceled,marked student as absent,pending'
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
    elif req.status_code == 416:
        return []


def find_specific_session(user_id,
                          authorization, status, after) -> Union[dict, Tuple]:
    """
    Find all session in the range
    :param after: date : after a date format: Y-m-dTHH:mm:ssZ
    :param status: str : pending, completed ....
    :param user_id: str : mentor id
    :param authorization: str:  Bearer Token
    :return: list of session, nb of session from parameter  Content Range
    """
    url = 'https://api.openclassrooms.com/users/'
    before = (after + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    after = (after - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    suffix = str(
        user_id) + '/sessions?actor=expert&life-cycle-status=' + status + '&after=' + after + '&before=' + before
    headers = {'Authorization': authorization,
               'Content-Type': 'application/json',
               'Connection': 'keep-alive',
               'X-Requested-With': 'XMLHttpRequest'}
    req = requests.get(url + suffix, headers=headers)
    if req.status_code == 200:
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


def schedule_meeting(schedule: SessionScheduleRequestModel, cookie):
    """
    Schedule a meeting on a date with a student
    :param schedule: SessionScheduleRequestModel
    :param cookie: str to interact with oc website
    :return: request
    """
    url = "https://openclassrooms.com/api/mentorship-sessions"

    headers = {"Content-Type": "text/plain;charset=UTF-8",
               'Connection': 'keep-alive',
               'X-Requested-With': 'XMLHttpRequest'}
    req = requests.post(url, cookies={"PHPSESSID": cookie}, headers=headers, data=schedule.json())
    if req.status_code == 201 or req.status_code == 400 or req.status_code == 409 or req.status_code == 403:
        return req
