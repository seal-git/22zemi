from app import my_app
from flask import render_template


@my_app.route('/')
def view_top():
    return render_template("index.html")


@my_app.route('/reverse')
def view_reverse():
    return render_template("reverse.html")


@my_app.route('/random')
def view_random():
    return render_template("random.html")

