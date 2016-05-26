import requests
from Webtech3Opdracht.settings import GITHUB_APP_ID, GITHUB_API_SECRET
from django.http import Http404


def get_access_token(code):
    """ Exchange code for an access token
    more info: developer.github.com/v3/oauth/    (see step 2)
    """
    params = {
        'client_id': GITHUB_APP_ID,
        'client_secret': GITHUB_API_SECRET,
        'code': code
    }
    headers = {'accept': 'application/json'}
    req = requests.post(GITHUB_GET_TOKEN_URL, params=params, headers=headers)

    if not req.ok:
        raise Http404

    try:
        access_token = req.json()['access_token']
    except KeyError:
        raise Http404

    return access_token