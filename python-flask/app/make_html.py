#make html page when app starts from yml
import yaml
from app import my_app, db


with open("app/yaml/articles.yml", "r") as yml:
    index_yml = yaml.safe_load(yml)

with open("app/templates/articles.html", "w") as f:
    for article in index_yml:
        title = article["title"]
        link = article["link"]
        description = article["description"]
        try:
            img = article["img"]
        except:
            img = "/static/images/noimage.png"
        try:
            img_alt = article["img_alt"]
        except:
            img_alt = "noimage"


        html_template = f'''\
        <article class="app-content">
            <a href="{link}">
            <div class="article-inner">
                <div class="article-pic">
                    <img src="{img}" alt="{img_alt}">
                </div>
                <div class="article-detail">
                    <header>
                        <h1 class="article-title">{title} </h1>
                    </header>
                    <p class="article-description">{description}</p>
                </div>
            </div>
            </a>
        </article>
        '''
        f.write(html_template)



