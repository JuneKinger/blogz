from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:june@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(240))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog')
def posts():

    # get the id from the browser <a href='/blog?id={{ blog.id }}'>{{ blog.title }}</a> from blog.html
    blog_id = (request.args.get('id'))
    
    # render the form the first time
    if blog_id is None:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build-a-blog", blogs=blogs)

    # render the form after a blog title is clicked
    blogs = Blog.query.get(blog_id)
    return render_template('display.html', blogs=blogs)
    
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    # if user enters a new post
    if request.method == 'POST':

        # initialize error variables
        title_err = ''
        body_err = ''    
        blog_title = ''
        blog_body = ''
        # request.form takes name= from the html file as an argument
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
 
        # check if blog title or blog body is left empty       
        if not blog_title or blog_title.strip() == '':
            title_err = 'Please fill in the title'

        if not blog_body or blog_body.strip() == '':
            body_err = 'Please fill in the body'

        if not title_err and not body_err:
            # create a new object blogs from inputs submitted and add to database
            blogs = Blog(blog_title, blog_body)
            db.session.add(blogs)
            db.session.commit()
            return redirect('/blog?id={}'.format(blogs.id))
        else:
            return render_template("newpost.html", blog_title=blog_title, blog_body=blog_body, title_err=title_err, body_err=body_err)

    # render on a GET request - the first time the form is rendered
    return render_template("newpost.html")  
    
if __name__ == "__main__":
    app.run()