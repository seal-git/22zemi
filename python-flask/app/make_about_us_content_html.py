from app import my_app, db
import markdown

print("making about-us-content.html")

md = markdown.Markdown()
with open("app/md/about-us-content.md", "r") as f:
    content = f.read()

content = md.convert(content)
with open("app/templates/about-us-content.html", "w") as f:
    f.write(content)