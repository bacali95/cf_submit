import hashlib
import os
import time

import requests

from .cf_utils import Obj, read_data_from_file, random_digits_string

cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
config_loc = os.path.join(cache_loc, 'config.json')


def generateAPISig(method, params):
    config = Obj(read_data_from_file(config_loc))
    if hasattr(config, 'api') and hasattr(config.api, 'key') and hasattr(config.api, 'secret'):
        api_key = config.api.key
        api_secret = config.api.secret
        unix_time = int(time.time())
        params.update({
            'apiKey': api_key,
            'time': unix_time,
        })
        r_string = random_digits_string(6)
        params_list = sorted([(key, params[key])
                              for key in params], key=lambda x: (x[0], x[1]))
        params_string = '&'.join(map(lambda x: '%s=%s' % (x[0], x[1]), params_list))
        to_be_encrypted = '%s%s?%s#%s' % (
            r_string, method, params_string, api_secret)
        return r_string + hashlib.sha512(to_be_encrypted.encode('utf-8')).hexdigest()
    else:
        return None


class CodeforcesAPI:
    baseUrl = 'https://codeforces.com/api'

    def contestList(self):
        response = requests.get('{}/contest.list'.format(self.baseUrl))
        return [Obj(res) for res in response.json()['result']]

    def contestStandings(self, contest_id, from_=1, count=10, show_unofficial=False):
        response = requests.get('{}/contest.standings'.format(self.baseUrl), params={
            'contestId': contest_id,
            'from': from_,
            'count': count,
            'showUnofficial': show_unofficial
        })
        return Obj(response.json()['result'])

    def contestHacks(self, contest_id):
        response = requests.get('{}/contest.hacks'.format(self.baseUrl), params={
            'contestId': contest_id
        })
        return [Obj(res) for res in response.json()['result']]

    def gymList(self):
        response = requests.get('{}/contest.list'.format(self.baseUrl), params={
            'gym': True
        })
        return [Obj(res) for res in response.json()['result']]

    def userSubmissions(self, handle, from_=1, count=100):
        params = {
            'handle': handle,
            'from': from_,
            'count': count,
        }
        api_sig = generateAPISig('/user.status', params)
        if api_sig is not None:
            params.update({'apiSig': api_sig})
        response = requests.get('{}/user.status'.format(self.baseUrl), params=params)
        return [Obj(res) for res in response.json()['result']]
