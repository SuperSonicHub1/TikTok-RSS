from extensions import MediaContent, Webfeeds, MediaItem, WebfeedsIcon
from datetime import datetime
from json import loads
from typing import List
from requests import Session
from rfeed import Item, Feed, Guid, Image
from selectolax.parser import HTMLParser
from flask import render_template

session = Session()
session.headers.update(
	{
		"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 13904.66.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
		"cookie": "tt_webid_v2=6941005984346588677; tt_webid=6941005984346588677; MONITOR_WEB_ID=6941005984346588677; tt_csrf_token=gJkjqyHS__rdz-9HJ0aLkqGW; R6kq3TV7=AALEAIF6AQAAkyrVOHTt0Vv47Eapl_SvwPdMQO8g1h36jfvBv8lkgIbqY-sP|1|0|4ddde2f765faf691eae484be3d34b83e3925b6c9; csrf_session_id=c98afccb7faf4e818e9c701aac3db0cd; s_v_web_id=verify_kqth5epk_FYyhpcfW_JD6M_41AC_Bv7h_4imih6DfHR68; bm_sz=B93B9EE44607F29E4EB6C7F158F63570~YAAQvqgmF3MrqnZ6AQAApsgAgQzthVQ9CBI8NnDxkgoSNW45JeHzP+Y3SkL56cF1z7+gDiSz6qm4BG/knNrGSpo3PS8eOT53JYpS2UFWduSbi94I8+T8o1wks3Di6IRQuuQJvm7vGCnmv88iXVGqoHyS0T9uBzh7L5K7FjveaUPiuvzzioCVHoSetqXXM+zf; _abck=A10BD0323F91881E35C263B571947C60~0~YAAQvqgmF3QrqnZ6AQAApsgAgQa53Bmrqo82bZTzilLGJa2ck9q2bpHcs1Kz+VNlXAOdMsASWJCecBln+D72HSAyKqojDOHDUw/3MIu6dyxupRWWpqb30nOnDfOQ2l5WtT9sJcRLV7067V6Jst6rMqHZ2ERp+Juy8kP2PoaJk3ISigG1f6yh0vxRuinOr5VePkeQEc4fduLFTnkQVUGqzrOhGQCzNLRjbpkjG4apP4eQdglyeLVUcR6f3EACLqARdPLAQyx0220GKhf4P+o4Nr+f+jPGekBgNFYd2fsGQtBuVm+qiTF5EQROOb25oR9Uw8GhvP/0J3znodc1nmxB+DBn8yb02LdXmudhTCIB0z3b+X630gUNy7cfeiZVxJof+HwL1SkBtP+fbFMVhuT5NUCGUHn/LG0=~-1~-1~-1; ttwid=1%7CviV24vZJLKgr3Ho7uiQLDwXAFgqgcMxNBSDsmDdflno%7C1625669097%7Cf1d36341b2a470e480a87668e8f505f48284ba5594f2a0f50dff25ebeb0c9ae7"
	}
)

URL = "https://www.tiktok.com/@{}"
VIDEO_URL = "https://www.tiktok.com/@{}/video/{}"

def generate_feed(username: str) -> Feed:
	username = username.lower()

	res = session.get(URL.format(username))
	res.raise_for_status()
	text = res.text

	tree = HTMLParser(text)

	json_element = tree.css_first("script#__NEXT_DATA__")
	next_data = loads(json_element.text())
	page_props = next_data.get("props", {}).get("pageProps", {})

	items: List[Item] = []

	posts = page_props.get("items", [])
	for post in posts:
		item_info = {}
		
		post_description = post.get("desc")
		item_info["title"] = post_description

		post_id = post.get("id")
		post_url = VIDEO_URL.format(username, post_id)
		item_info["link"] = post_url
		item_info["guid"] = Guid(post_url)

		post_date = post.get("createTime")
		item_info["pubDate"] = datetime.fromtimestamp(post_date)

		post_author = post.get("author", {}).get("uniqueId")
		item_info["author"] = "@" + post_author

		description = render_template("description.html", post=post)
		item_info["description"] = description

		post_cover = post.get("video", {}).get("originCover")
		if post_cover:
			media_item = MediaItem(
				post_cover,
				'image/jpeg',
				'image',
				True,
			)
			item_info["extensions"] = [media_item]
		
			item = Item(**item_info)
			items.append(item)
		
	user = page_props.get("userInfo", {}).get("user", {})

	nickname = user.get("nickname")
	signature = user.get("signature")
	bio_link = user.get("bioLink", {}).get("link")
	avatar_url = user.get("avatarLarger") or user.get("avatarMedium") or user.get("avatarThumb")
	link=URL.format(username)

	image = Image(
		avatar_url,
		f"Avatar image for @{username}",
		link
	)
	icon = WebfeedsIcon(avatar_url)

	feed = Feed(
		title=f"{nickname} - {username}",
		link=link,
		description=f"{signature} || {bio_link}",
		items=items,
		image=image,
		lastBuildDate=datetime.now(),
		extensions=[
			MediaContent(),
			Webfeeds(), 
			icon
		]
	)

	return feed
