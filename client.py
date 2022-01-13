import random
import re
import string
import time
from requests import Session, Response


session = Session() 
session.headers.update({})

# yt-dlp's constants
# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/tiktok.py#L29-L35
APP_VERSION = '20.1.0'
MANIFEST_APP_VERSION = '210'
APP_NAME = 'trill'
AID = 1180
API_HOSTNAME = 'api-h2.tiktokv.com'
UPLOADER_URL_FORMAT = 'https://www.tiktok.com/@%s'
WEBPAGE_HOST = 'https://www.tiktok.com/'

# My constants
URL = WEBPAGE_HOST + "@{}"
VIDEO_URL = URL + "/video/{}"

def get_user_id(username: str) -> str:
	res = session.get(URL.format(username), headers={
			'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
		}
	)
	return re.search(r'snssdk\d*://user/profile/(\d+)', res.text).group(1)

def call_api(path: str, params: dict) -> Response:
	"""
	https://github.com/yt-dlp/yt-dlp/blob/b31874334d5d68121a4a3f0d28dc1b39e5fca93b/yt_dlp/extractor/tiktok.py#L38-L84
	"""
	params = {
		**params,
		'version_name': APP_VERSION,
		'version_code': MANIFEST_APP_VERSION,
		'build_number': APP_VERSION,
		'manifest_version_code': MANIFEST_APP_VERSION,
		'update_version_code': MANIFEST_APP_VERSION,
		'openudid': ''.join(random.choice('0123456789abcdef') for _ in range(16)),
		'uuid': ''.join([random.choice(string.digits) for _ in range(16)]),
		'_rticket': int(time.time() * 1000),
		'ts': int(time.time()),
		'device_brand': 'Google',
		'device_type': 'Pixel 4',
		'device_platform': 'android',
		'resolution': '1080*1920',
		'dpi': 420,
		'os_version': '10',
		'os_api': '29',
		'carrier_region': 'US',
		'sys_region': 'US',
		'region': 'US',
		'app_name': APP_NAME,
		'app_language': 'en',
		'language': 'en',
		'timezone_name': 'America/New_York',
		'timezone_offset': '-14400',
		'channel': 'googleplay',
		'ac': 'wifi',
		'mcc_mnc': '310260',
		'is_my_cn': 0,
		'aid': AID,
		'ssmix': 'a',
		'as': 'a1qwert123',
		'cp': 'cbfhckdckkde1',
	}
	session.cookies.set(
		"odin_tt",
		''.join(random.choice('0123456789abcdef') for _ in range(160)),
		domain=API_HOSTNAME
	)
	sid_tt = session.cookies.get("sid_tt", domain=WEBPAGE_HOST)
	if sid_tt:
		session.cookies.set(
			"sid_tt",
			sid_tt,
			domain=API_HOSTNAME
		)
	return session.get(f"https://{API_HOSTNAME}/aweme/v1/{path}/",headers={
			'User-Agent': f'com.ss.android.ugc.trill/{MANIFEST_APP_VERSION} (Linux; U; Android 10; en_US; Pixel 4; Build/QQ3A.200805.001; Cronet/58.0.2991.0)',
			'Accept': 'application/json',
		},
		params=params
	)

def get_user(username: str) -> Response:
	"""
	https://github.com/yt-dlp/yt-dlp/blob/b31874334d5d68121a4a3f0d28dc1b39e5fca93b/yt_dlp/extractor/tiktok.py#L529-L539
	"""
	user_id = get_user_id(username)
	params = {
		'user_id': user_id,
		'count': 21,
		'max_cursor': 0,
		'min_cursor': 0,
		'retry_type': 'no_retry',
		# Some endpoints don't like randomized device_id, so it isn't directly set in _call_api.
		'device_id': ''.join(random.choice(string.digits) for _ in range(19)),
	}
	return call_api("aweme/post", params)

if __name__ == "__main__":
	print(get_user("emiru").json())
