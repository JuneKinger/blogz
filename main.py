from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:june@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = '#fdfaf!afagpo@dmnfah%'
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(240))
    body = db.Column(db.Text)
    
    # foreign key owner_id links user.id to the blog post
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

    ''' Each Blog object has an owner associated with it 
    (passed to it in the constructor), so you can access the
     properties of that owner (such as username, or id) owner.username
     and owner.id with dot notation (above and below) '''
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner



class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))

    ''' signifies a relationship between the blog table and the user,
    thus binding this user with the blog posts they write '''
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
 
    allowed_routes = ['login', 'list_blogs', 'index', 'signup']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

        
@app.route('/')
def index():

    users = User.query.all()
    return render_template("index.html", users=users)
 

@app.route('/blog', methods=['GET'])
def list_blogs():

    ''' check if browser query parameter is 'user' or 'id'
    that is <a href='/blog?id={{ blog.id }}'>{{ blog.title }}</a> from blog.html
    or <a href='/blog?user={{ user.id }}'>{{ user.username }}</a> from blog.html
    if parameter is 'user' '''

    # also value of request.args.get() is None if either 'id' or 'user' is 
    # not applicable. That's why it does not error out
    blog_id = request.args.get('id')
    username = (request.args.get('user'))
    
    # owner is an object that can be used, for eg, as owner.id or searching
    # tables with owner object, eg blogs = Blog.query.filter_by(owner=owner).all()
    owner = User.query.filter_by(username=username).first()

    if request.args.get('user'):

        # EITHER get all the blog posts where column owner_id from blog table
        # = id from object owner above         
        # blogs = Blog.query.filter_by(owner_id=owner.id).all()
        # OR 
        # blogs = Blog.query.filter_by(owner=owner).all()
        blogs = Blog.query.filter_by(owner=owner).all()
        return render_template('blog.html', blogs=blogs)
    
    # get the variable id from the dictionary request.args 
    elif request.args.get('id'):

        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('blog.html', blogs=blogs) 
      
    else:
        # render the form the first time
        if not blog_id:

            blogs = Blog.query.all()

            # I can only send blogs across to blog.html (and don't need owner)
            # because blogs and owner relationship is already established in backref = 'owner'
            return render_template('blog.html', blogs=blogs)


@app.route('/login', methods=['POST', 'GET'])
def login():


    if request.method=='POST':

        username = request.form['user_name']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        # if user exists, compare password
        if user:
            if user.password == password: 
                # makes a key:value pair in session
                session['username'] =  username

                flash("Logged in", "error")
                return redirect('/newpost')
            else:
                passwd_err = "Invalid password"
                return render_template('login.html', passwd_err=passwd_err)
        else:
                user_name_err = "Invalid Username"
                return render_template('login.html', user_name_err=user_name_err)

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    user_name_err = ''
    passwd_err = ''
    verify_passwd_err = ''

    if request.method=='POST':

        user_name = request.form['user_name']
        passwd = request.form['passwd']
        verify_passwd = request.form['verify_passwd']

        # check if user exists
        existing_user = User.query.filter_by(username=user_name).first()

        if existing_user:
            user_name_err = "Duplicate user"
            return render_template("signup.html", name=user_name, 
                user_name_err=user_name_err, passwd_err=passwd_err, 
                verify_passwd_err=verify_passwd_err)

        #validate user's data, password=verify_password, etc
        if user_name == '' or len(user_name) < 3 or ' ' in user_name:
            user_name_err = 'Invalid Username'

        if passwd == '' or ' ' in passwd or len(passwd) < 3:
            passwd_err = 'Invalid Password'

        if verify_passwd != passwd:
            verify_passwd_err = "Passwords do not match"

        # if errors found
        if user_name_err or passwd_err or verify_passwd_err:

            return render_template("signup.html", name=user_name, 
                 user_name_err=user_name_err, passwd_err=passwd_err, 
                 verify_passwd_err=verify_passwd_err)
        else:
            # if no errors found, add to db
            new_user = User(user_name, passwd)
            db.session.add(new_user)
            db.session.commit()
            session['new_user'] =  new_user.username
            return redirect('/newpost')

    return render_template('signup.html', user_name_err=user_name_err, 
passwd_err=passwd_err, verify_passwd_err=verify_passwd_err)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    # if user enters a new post
    if request.method == 'POST':

        # initialize error variables
        title_err = ''
        body_err = ''    
        blog_body = ''
        blog_owner = ''

        # get the username out of the session, then filter the user result set 
        # by that username and get the first one (should only be one 
        # since usernames are unique) and place it in owner (object) to
        # add to db
        owner = User.query.filter_by(username=session['username']).first()

        # request.form takes name= from the html file as an argument
        blog_title = request.form["blog_title"]
        blog_body = request.form['blog_body']
 
        # check if blog title or blog body is left empty       
        if not blog_title or blog_title.strip() == '':
            title_err = 'Please fill in the title'

        if not blog_body or blog_body.strip() == '':
            body_err = 'Please fill in the body'

        if not title_err and not body_err:
            # create a new object blogs from inputs submitted and add to database
            blogs = Blog(blog_title, blog_body, owner)
            db.session.add(blogs)
            db.session.commit()
            title_err = ''
            body_err = ''    
            return redirect('/blog?id={}'.format(blogs.id))

        else:
            return render_template("newpost.html", blog_title=blog_title, blog_body=blog_body, title_err=title_err, body_err=body_err)

    # render on a GET request - the first time the form is rendered
    return render_template("newpost.html")  


@app.route('/logout')
def logout():
    del session['username']        
    return redirect('/blog')


if __name__ == "__main__":
    app.run()