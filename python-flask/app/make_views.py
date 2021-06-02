#make views.py from yml when app starts
import yaml
import re
from pathlib import Path
from app import my_app, db


print("making views.py")

with open("app/yaml/articles.yml", "r") as yml:
    index_yml = yaml.safe_load(yml)

with open("app/views.py", "w") as f:
    init_script = '''\
from app import my_app
from flask import render_template
    
    
@my_app.route('/')
def view_top():
    return render_template("index.html")
    
@my_app.route('/about-us')
def view_about_us():
    return render_template("about-us.html")
    
    '''
    f.write(init_script)
    for article in index_yml:
        title = re.sub(r"-", r"_", article["title"])
        link = article["link"]
        html = article["html"]
        p = Path("app/templates/"+html)
        if not p.exists():
            raise(html + "does not exist!")

        render_script = f'''
@my_app.route('{link}')
def view_{title}():
    return render_template("{html}")
        '''
        f.write(render_script)



