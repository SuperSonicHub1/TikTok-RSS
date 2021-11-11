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
		"Cookie": "ttwid=1%7CuoFxMFwD7cIr1UgfoWY1CkMaxgvlFuuzJXJumW4pWOg%7C1636671701%7C5b14214c63cac0fb13153c055d9ab8f68f7378e138b1f5b18b2aabfcedb70c9e; tt_csrf_token=XNJBGbknozs5RDpGMT1gHIvp; R6kq3TV7=ALrgOBF9AQAAcTHLDnoRquLN-4xk0P_GRyXGzm62HEvTmBOtvSM_EOSjB21W|1|0|53ae1d21a766ab90d5503f5a55246d071f601ae9; s_v_web_id=verify_kvvjxx5n_ujXwTACt_wsTY_4F4v_8EVj_sXAbvlVqQ97k"
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
