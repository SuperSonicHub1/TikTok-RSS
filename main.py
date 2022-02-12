from generator import generate_feed
from flask import Flask, redirect, make_response, render_template, url_for, request
from requests import HTTPError
from http import HTTPStatus

app = Flask(__name__)

@app.errorhandler(HTTPError)
def handle_request_error(e: HTTPError):
	if e.response.status_code == HTTPStatus.NOT_FOUND:
		return "Supplied user could not be found", HTTPStatus.NOT_FOUND

@app.route("/favicon.ico")
def favicon():
	return redirect("https://s16.tiktokcdn.com/musical/resource/mtact/static/images/logo_144c91a.png?v=2")

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/feed/<username>")
def feed(username: str):
	feed = generate_feed(username)
	response = make_response(feed.rss())
	response.headers.set('Content-Type', 'application/rss+xml')
	return response

@app.route('/lookup')
def lookup():
	return redirect(url_for('feed', username=request.args.get("q")))

app.run(host='0.0.0.0',port=8080)
