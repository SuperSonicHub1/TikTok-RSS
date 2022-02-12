import client
from extensions import MediaContent, Webfeeds, MediaItem, WebfeedsIcon
from datetime import datetime
from rfeed import Item, Feed, Guid, Image
from flask import render_template, abort

def get_author(items: list) -> dict:
	authors = list(
		filter(
			bool,
			map(
				lambda item: item.get("author"),
				items,
			),
		),
	)
	return authors[0] if authors else {}

def generate_item(item: dict, author: dict) -> Item:
	item_info = {}

	username = author.get("unique_id")

	description = item.get("desc")
	item_info["title"] = description

	post_id = item.get("aweme_id")
	post_url = client.VIDEO_URL.format(username, post_id)
	item_info["link"] = post_url
	item_info["guid"] = Guid(post_url)

	post_date = item.get("create_time")
	item_info["pubDate"] = datetime.fromtimestamp(post_date)

	item_info["author"] = author.get("nickname")

	description = render_template("description.html", post=item)
	item_info["description"] = description

	post_cover = item.get("video", {}).get("origin_cover")
	if post_cover:
		media_item = MediaItem(
			post_cover["url_list"][0],
			'image/jpeg',
			'image',
			True,
		)
		item_info["extensions"] = [media_item]
	
		item = Item(**item_info)

	return Item(**item_info)

def generate_feed(username: str) -> Feed:
	body = client.get_user(username.lower())
	aweme_list = body.get("aweme_list", [])
	if not aweme_list:
		abort(404)
	author = get_author(aweme_list)
	items = map(
		lambda item: generate_item(item, author),
		aweme_list,
	)

	nickname = author.get("nickname")
	signature = author.get("signature")
	avatar_url = author.get("avatar_larger", {}).get("url_list", [None])[0]
	link = client.URL.format(username)

	image = Image(
		avatar_url,
		f"Avatar image for {nickname}",
		link
	)
	icon = WebfeedsIcon(avatar_url)

	feed = Feed(
		title=f"{nickname} - {username}",
		link=link,
		description=f"{signature}",
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
