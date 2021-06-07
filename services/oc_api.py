import re

import requests


def get_range(r_min, r_max, step=19):
    output = []
    complete_range = (r_max - r_min) // step
    for i in range(complete_range):
        output.append((i * (step + 1),
                       (i + 1) * step + 1))
    if (r_max - r_min) % step != 0:
        output.append((complete_range * (step + 1), r_max - 1))
    return output


def login_oc(mail, pwd):
    req = requests.get('https://openclassrooms.com/fr/login_ajax')

    cookies = {"PHPSESSID": req.cookies['PHPSESSID']}
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
    else:
        return {"state": True, "token": req.cookies['access_token']}


def get_token():
    pass


def update_session_api(range_min, range_max, authorization, return_range=False):
    """
    Find all session in the range
    :param range_min: int
    :param range_max:  int
    :return: list of session, nb of session from parameter  Content Range
    """
    url = 'https://api.openclassrooms.com/users/'
    suffix = '9490184/sessions?life-cycle-status=canceled,completed,late canceled,marked student as absent'
    headers = {'Authorization': authorization,
               'Content-Type': 'application/json',
               'Range': 'items=' + str(range_min) + "-" + str(range_max),
               'Connection': 'keep-alive',
               'X-Requested-With': 'XMLHttpRequest'}
    req = requests.get(url + suffix, headers=headers)
    if req.status_code == 206:
        if return_range:
            return req.json(), int(req.headers['Content-Range'].split('/')[-1])
        else:
            return req.json()


def get_student_type(student_id, session_id):
    rx_student_status = re.compile(r'<div class="mentorshipStudent__details oc-typography-body1"><p>([^<]+)</p>')

    url = 'https://openclassrooms.com/' + 'fr/mentorship/students/' + str(student_id) + '/dashboard'

    req = requests.get(url, cookies={"PHPSESSID": session_id})
    if req.status_code != 200:
        raise RuntimeError(f'{req.url} returned {req.status_code}')

    html = req.text.replace('\n', '')
    match_status = rx_student_status.search(html)
    if match_status is not None:
        return {"status": match_status.group(1).strip()}
