from app import my_app
from flask import render_template
    
    
@my_app.route('/')
def view_top():
    return render_template("index.html")
    
    
    
@my_app.route('/reverse')
def view_reverse():
    return render_template("reverse.html")
        
@my_app.route('/is-it-sentence')
def view_is_it_sentence():
    return render_template("is-it-sentence.html")
        
@my_app.route('/random')
def view_random():
    return render_template("random.html")
        
@my_app.route('/db-sample')
def view_db_sample():
    return render_template("db-sample.html")
        