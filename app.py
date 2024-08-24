from flask import Flask, render_template, session, redirect, url_for
from markupsafe import escape

app = Flask(__name__)
app.secret_key = 'e4ed89f02f3aa07a4309daaadb454bfff'

@app.route("/")
def index():
	return render_template('index.html')

@app.route('/stack')
def stack():
	folders = {
		"ngc7000": ["light", "dark", "flat", "bias"],
		"test222": ["light", "dark", "flat", "bias"],
		"ic1234": ["light", "dark", "flat", "bias"],
		"m1": ["light", "dark", "flat", "bias"],
	}

	return render_template('stack.html', folders=folders)

@app.route('/about')
def about():
	return render_template('about.html')