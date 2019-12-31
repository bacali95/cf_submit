import os
import time
import hashlib
import requests

from .cf_utils import obj, readDataFromFile, randomDigitsString

cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
config_loc = os.path.join(cache_loc, 'config.json')


def generateAPISig(method, params):
    config = obj(readDataFromFile(config_loc))
    if hasattr(config, 'api') and hasattr(config.api, 'key') and hasattr(config.api, 'secret'):
        apiKey = config.api.key
        apiSecret = config.api.secret
        unixTime = int(time.time())
        params.update({
            'apiKey': apiKey,
            'time': unixTime,
        })
        rString = randomDigitsString(6)
        paramsList = sorted([(key, params[key])
                             for key in params], key=lambda x: (x[0], x[1]))
        paramsString = '&'.join(map(lambda x: '%s=%s' %
                                    (x[0], x[1]), paramsList))
        toBeCrypted = '%s%s?%s#%s' % (
            rString, method, paramsString, apiSecret)
        return rString + hashlib.sha512(toBeCrypted.encode('utf-8')).hexdigest()
    else:
        return None


class CodeforcesAPI:
    baseUrl = 'https://codeforces.com/api'

    def contestList(self):
        response = requests.get('{}/contest.list'.format(self.baseUrl))
        return [obj(res) for res in response.json()['result']]

    def contestStandings(self, contestId, from_=1, count=10, showUnofficial=False):
        response = requests.get(
            '{}/contest.standings'.format(self.baseUrl), params={
                'contestId': contestId,
                'from': from_,
                'count': count,
                'showUnofficial': showUnofficial
            })
        return obj(response.json()['result'])

    def contestHacks(self, contestId):
        response = requests.get(
            '{}/contest.hacks'.format(self.baseUrl), params={
                'contestId': contestId
            })
        return [obj(res) for res in response.json()['result']]

    def gymList(self):
        response = requests.get(
            '{}/contest.list'.format(self.baseUrl), params={
                'gym': True
            })
        return [obj(res) for res in response.json()['result']]

    def userSubmissions(self, handle, from_=1, count=100):
        params = {
            'handle': handle,
            'from': from_,
            'count': count,
        }
        apiSig = generateAPISig('/user.status', params)
        if apiSig is not None:
            params.update({'apiSig': apiSig})
        response = requests.get(
            '{}/user.status'.format(self.baseUrl), params=params)
        return [obj(res) for res in response.json()['result']]
