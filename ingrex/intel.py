"Ingrex is a python lib for ingress"
import requests
import re
import json


class Intel(object):
    "main class with all Intel functions"

    @property
    def cookie(self):
        return self.cookie

    @cookie.setter
    def cookie(self, cookies):
        token = re.findall(r'csrftoken=(\w*);', cookies)[0]
        self.headers = {
            'accept-encoding': 'gzip, deflate',
            'content-type': 'application/json; charset=UTF-8',
            'cookie': cookies,
            'origin': 'https://www.ingress.com',
            'referer': 'https://www.ingress.com/intel',
            'user-agent': 'Mozilla/5.0 (MSIE 9.0; Windows NT 6.1; Trident/5.0)',
            'x-csrftoken': token,
        }

    def __init__(self, field, cookies=None, credential=None, phantom_path=None, phantom_args=None, proxies=None):
        self.DEBUG = False
        self.credential = credential
        self.field = {
            'maxLatE6': field['maxLatE6'],
            'minLatE6': field['minLatE6'],
            'maxLngE6': field['maxLngE6'],
            'minLngE6': field['minLngE6'],
        }
        self.point = {
            'latE6': (field['maxLatE6'] + field['minLatE6']) >> 1,
            'lngE6': (field['maxLngE6'] + field['minLngE6']) >> 1,
        }
        self.phantom_path = phantom_path
        self.phantom_args = phantom_args
        self.session = requests.session()
        self.session.proxies = proxies
        if cookies is not None:
            self.cookie = cookies
        elif credential is not None:
            self.fetch_cookie()
        else:
            raise CredentialError()
        self.refresh_version()


    def fetch_cookie(self):
        if self.credential is None:
            return
        from selenium import webdriver
        import time
        # get a new cookie for this program
        if self.phantom_path is not None:
            driver = webdriver.PhantomJS(self.phantom_path, service_args=self.phantom_args)
        else:
            driver = webdriver.PhantomJS(service_args=self.phantom_args)
        driver.get('https://www.ingress.com/intel')
        # get the login page
        link = driver.find_elements_by_tag_name('a')[0].get_attribute('href')
        driver.get(link)
        if self.DEBUG:
            driver.get_screenshot_as_file('1.png')
        # simulate manual login
        driver.set_page_load_timeout(10)
        driver.set_script_timeout(20)
        driver.find_element_by_id('Email').send_keys(self.credential[0])
        driver.find_element_by_css_selector('#next').click()
        time.sleep(3)
        if self.DEBUG:
            driver.get_screenshot_as_file('2.png')
        driver.find_element_by_id('Passwd').send_keys(self.credential[1])
        driver.find_element_by_css_selector('#signIn').click()
        time.sleep(3)
        if self.DEBUG:
            driver.get_screenshot_as_file('3.png')
        # get the cookies
        temp = driver.get_cookies()
        self.cookie = ';'.join(['{0}={1}'.format(x["name"], x["value"]) for x in temp])
        driver.quit()

    def refresh_version(self):
        "refresh api version for request"
        request = self.session.get('https://www.ingress.com/intel', headers=self.headers)
        self.version = re.findall(r'gen_dashboard_(\w*)\.js', request.text)[0]

    def fetch(self, url, payload):
        "raw request with auto-retry and connection check function"
        payload['v'] = self.version
        count = 0
        while count < 3:
            try:
                request = self.session.post(url, data=json.dumps(payload), headers=self.headers)
                return request.json()['result']
            except requests.ConnectionError:
                raise IntelError
            except ValueError:
                count += 1
                self.fetch_cookie()
                continue
            except Exception:
                count += 1
                continue
        raise CookieError

    def fetch_msg(self, mints=-1, maxts=-1, reverse=False, tab='all'):
        "fetch message from Ingress COMM, tab can be 'all', 'faction', 'alerts'"
        url = 'https://www.ingress.com/r/getPlexts'
        payload = {
            'maxLatE6': self.field['maxLatE6'],
            'minLatE6': self.field['minLatE6'],
            'maxLngE6': self.field['maxLngE6'],
            'minLngE6': self.field['minLngE6'],
            'maxTimestampMs': maxts,
            'minTimestampMs': mints,
            'tab': tab
        }
        if reverse:
            payload['ascendingTimestampOrder'] = True
        return self.fetch(url, payload)

    def fetch_map(self, tilekeys):
        "fetch game entities from Ingress map"
        url = 'https://www.ingress.com/r/getEntities'
        payload = {
            'tileKeys': tilekeys
        }
        return self.fetch(url, payload)

    def fetch_portal(self, guid):
        "fetch portal details from Ingress"
        url = 'https://www.ingress.com/r/getPortalDetails'
        payload = {
            'guid': guid
        }
        return self.fetch(url, payload)

    def fetch_score(self):
        "fetch the global score of RESISTANCE and ENLIGHTENED"
        url = 'https://www.ingress.com/r/getGameScore'
        payload = {}
        return self.fetch(url, payload)

    def fetch_region(self):
        "fetch the region info of RESISTANCE and ENLIGHTENED"
        url = 'https://www.ingress.com/r/getRegionScoreDetails'
        payload = {
            'lngE6': self.point['lngE6'],
            'latE6': self.point['latE6'],
        }
        return self.fetch(url, payload)

    def fetch_artifacts(self):
        "fetch the artifacts details"
        url = 'https://www.ingress.com/r/getArtifactPortals'
        payload = {}
        return self.fetch(url, payload)

    def send_msg(self, msg, tab='all'):
        "send a message to Ingress COMM, tab can be 'all', 'faction'"
        url = 'https://www.ingress.com/r/sendPlext'
        payload = {
            'message': msg,
            'latE6': self.point['latE6'],
            'lngE6': self.point['lngE6'],
            'tab': tab
        }
        return self.fetch(url, payload)

    def send_invite(self, address):
        "send a recruit to an email address"
        url = 'https://www.ingress.com/r/sendInviteEmail'
        payload = {
            'inviteeEmailAddress': address
        }
        return self.fetch(url, payload)

    def redeem_code(self, passcode):
        "redeem a passcode"
        url = 'https://www.ingress.com/r/redeemReward'
        payload = {
            'passcode': passcode
        }
        return self.fetch(url, payload)


class IntelError(BaseException):
    """Intel Error"""


class CookieError(IntelError):
    """Intel Error"""


class CredentialError(IntelError):
    """Intel Error"""


if __name__ == '__main__':
    pass
