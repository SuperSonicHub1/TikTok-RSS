from generator import generate_feed
from flask import Flask, redirect, make_response, render_template, url_for, request

app = Flask(__name__)

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
