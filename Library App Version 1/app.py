# Importing work is here
import os

import matplotlib.pyplot as plt
from io import BytesIO
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from flask import Flask,render_template,request,redirect,url_for,flash,session,abort,send_file
from modal import * # importing from modal

############################################################################################################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Library.sqlite3" # Database connection for using database values
app.config['SECRET_KEY'] = 'secret' # Admin session available
app.config ['UPLOAD_FOLDER'] = 'static/uploads'
app.app_context().push()
db.init_app(app)
############################################################################################################

@app.route('/admin/dashboard', methods=["GET", "POST"])
def admin_dashboard():
    try:
        total_books = len(Book.query.all())
        available_books = len(Book.query.filter_by(availability=1).all())

        plt.figure(figsize=(8, 6))
        categories = ['Total Books', 'Available Books']
        values = [total_books, available_books]
        plt.bar(categories, values, color=['blue', 'green'])
        plt.title('Book Statistics')
        plt.xlabel('Category')
        plt.ylabel('Count')

        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)

        plt.clf()

        return send_file(image_stream, mimetype='image/png')
    except Exception as e:
        flash("An error occurred: {}".format(str(e)))
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/dash', methods=["GET", "POST"])
def admin_dash():
    try:
        sections = Section.query.all()
        section_names = [section.name for section in sections]
        book_counts = [len(section.books) for section in sections]

        plt.figure(figsize=(8, 6))
        plt.pie(book_counts, labels=section_names, autopct='%1.1f%%', startangle=140)
        plt.title('Books per Section')

        image_ = BytesIO()
        plt.savefig(image_, format='png')
        image_.seek(0)

        plt.clf()

        return send_file(image_, mimetype='image2/png')
    except Exception as e:
            flash("An error occurred: {}".format(str(e)))
            return redirect(url_for('admin_dash'))

# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


############################################################################################################
# Genres=['Pop','Rock','Hip&Hop','Rap','Country','R & B','Folk','Jazz','Heavy Metal','EDM','Soul','Funk','Raggae','Disco','Punk Rock','Classical','House','Techno','Indie Rock']
Languages=['Hindi','English','Punjabi','Marathi','Bengali']
Ratings = [1,2,3,4,5]
ALLOWED_EXTENSIONS = {'.png','.jpg','.jpeg','.ogg','.mp3'}

def verify_user(list1,email_address,password):
    for i in list1:
        if i.email_address == email_address and i.password==password:
            return 1
    return 0

# WEBPAGE Functions start from here
""" HOME PAGE"""
def login_user(user):
    session['user_id'] = user.id

def logout_user():
    session.pop('user_id', None)

def is_authenticated_user():
    return 'user_id' in session

@app.route('/dashboard/<int:n>', methods=["GET", "POST"])
def Dash(n):
    try:
        if not is_authenticated_user():
            flash("Please log in to access this page.")
            return redirect(url_for('Login'))
        cred = User.query.filter_by(id=n).first()
        if not cred:
            flash("Invalid user ID.")
            return redirect(url_for('Login'))
        biti = Book.query.all()
        cred2 = UserBook.query.filter_by(user_id=n).first()
        sort_order = request.args.get('sort_order', 'asc')

        if sort_order == 'asc':
            cred3 = sorted(biti, key=lambda x: x.name)
        elif sort_order == 'desc':
            cred3 = sorted(biti, key=lambda x: x.name, reverse=True)
        else:
            cred3 = biti

        return render_template('/user/dashboard.html', cred=cred, cred2=cred2, cred3=cred3)
    except Exception as e:
        flash("An error occurred: {}".format(str(e)))
        return redirect(url_for('Login'))

@app.route('/books/<int:n>',methods=["GET","POST"])
def Books(n):
    cred=User.query.filter_by(id=n).first()
    return render_template('/user/books.html',cred=cred)

@app.route('/sections/<int:n>', methods=["GET", "POST"])
def Sections(n):
    try:
        if is_authenticated_user():
            cred = User.query.filter_by(id=n).first()
            if not cred:
                abort(404)
            list1 = Section.query.all()
            sort_order = request.args.get('sort_order', 'asc')

            if sort_order == 'asc':
                list1 = sorted(list1, key=lambda x: x.name)
            elif sort_order == 'desc':
                list1 = sorted(list1, key=lambda x: x.name, reverse=True)
            else:
                list1 = list1

            return render_template('/user/sections.html', cred=cred, list1=list1)
        else:
            abort(404)
    except Exception as e:
        flash("An error occurred: {}".format(str(e)))
        abort(404)


@app.route('/feedback/<int:n>',methods=["GET","POST"])
def Feedbacks(n):
    cred=User.query.filter_by(id=n).first()
    if not cred:
        return redirect(url_for('Login'))
    list1=Book.query.all()
    return render_template('/user/feedback.html',cred=cred,list1=list1)

@app.route('/account/<int:n>',methods=["GET","POST"])
def Account(n):
    cred=User.query.filter_by(id=n).first()
    if not cred:
        return redirect(url_for('Login'))
    list1=cred.user_books
    list2=[]
    for i in list1:
        b2=Book.query.filter_by(id=i.book_id).first()
        list2.append(b2.name)
    return render_template('/user/account.html',cred=cred,list2=list2)

@app.route('/issue/<int:uid>/<int:bid>',methods=["GET","POST"])
def Issue(uid,bid):
    b=Book.query.filter_by(id=bid).first()
    sid=Section.query.filter_by(id=b.section_id).first()
    sid=sid.id
    u=User.query.filter_by(id=uid).first()
    if not u:
        return redirect(url_for('Login'))
    if b and u:
        u.token -= 1
        b.availability = 0
        t = datetime.datetime.now()
        result = t + datetime.timedelta(days=7)
        user_book = UserBook(user_id=uid, book_id=bid, issue_date=t, return_date=result)
        db.session.add(user_book)
        db.session.commit()
    return redirect(url_for('More',uid=uid,sid=sid))

@app.route('/return/<int:uid>/<int:bid>', methods=["GET", "POST"])
def Return(uid, bid):
    book = Book.query.filter_by(id=bid).first()
    sid=Section.query.filter_by(id=book.section_id).first()
    sid=sid.id
    user = User.query.filter_by(id=uid).first()
    if not user:
        return redirect(url_for('Login'))
    if book and user:
        user.token += 1
        book.availability = 1
        user_book = UserBook.query.filter_by(user_id=uid, book_id=bid).first()
        if user_book:
            db.session.delete(user_book)
        db.session.commit()
    return redirect(url_for('More',uid=uid,sid=sid))

@app.route('/more/<int:uid>/<int:sid>',methods=["GET","POST"])
def More(uid,sid):
    ucred=User.query.filter_by(id=uid).first()
    scred=Section.query.filter_by(id=sid).first()
    if not ucred or not scred:
        abort(404)
    Us=UserBook.query.all()
    list1=scred.books
    list2=[]
    for i in list1:
        list2.append(i.name)  
    return render_template('/user/books.html',list2=list1,cred=ucred,cred3=Us,cred5=scred)


@app.route('/open/<int:n>/<string:s>',methods=["GET","POST"])
def Open(n,s):
    uid=User.query.filter_by(id=n).first()
    book=Book.query.filter_by(name=s).first()
    if not uid or not book:
        abort(404)
    sec=book.section_id
    return render_template('/user/open.html',cred=uid,book=book)


@app.route('/search/<int:n>',methods=["GET","POST"])
def search(n):
    flag = True
    if request.method=="POST":
        flag = False
        i=0
        search_query = request.form.get('search_query', '')
        search_query2 = request.form.get('search_query2', '')
        if search_query:
            i=1
            cred3 = search_books(search_query)
            return render_template('/user/search.html', flag=flag, cred=User.query.filter_by(id=n).first(),cred3=cred3,i=i)
        elif search_query2:
            i=2
            cred3 = search_sections(search_query2)
            return render_template('/user/search.html', flag=flag, cred=User.query.filter_by(id=n).first(),cred3=cred3,i=i)
        else:
            flag = True
    return render_template('/user/search.html', flag=flag, cred=User.query.filter_by(id=n).first())

def search_books(search_query):
    return Book.query.filter(Book.name.ilike(f'%{search_query}%')).all()
def search_sections(search_query):
    return Section.query.filter(Section.name.ilike(f'%{search_query}%')).all()
#######################################################  Admin PARTS HERE ##########################################################

@app.route('/admin',methods=["GET","POST"])
def Admin():
    book=Book.query.all()
    ubook=UserBook.query.all()
    u=User.query.all()
    l=[]
    for i in u:
        l.append(i.id)
    g=[]
    for i in book:
        g.append(i.id)
    maxi2=max(g)
    maxi=max(l)
    use=User.query.filter_by(id=maxi).first()
    use2=Book.query.filter_by(id=maxi2).first()
    return render_template('/admin/admin_home.html',book=book,ubook=ubook,use=use,use2=use2,user=u)

@app.route('/abook',methods=["GET","POST"])
def Abook():
    list1=Book.query.all()
    return render_template('/admin/admin_book.html',list1=list1)

@app.route('/auser',methods=["GET","POST"])
def Auser():
    list1=User.query.all()
    return render_template('/admin/admin_user.html',list1=list1)

@app.route('/afeedback',methods=["GET","POST"])
def Afeedback():
    list1=Feedback.query.all()
    return render_template('/admin/admin_feedback.html',list1=list1)

@app.route('/asection',methods=["GET","POST"])
def Asection():
    list1=Section.query.all()
    return render_template('/admin/admin_section.html',list1=list1)



#######################################################  ADDING PARTS HERE ##########################################################
@app.route('/addbook', methods=["GET", "POST"])
def Add_book():
    try:
        if request.method == "POST":
            name = request.form.get('title')
            content = request.files['location']
            filename1 = secure_filename(content.filename)
            file_path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
            content.save(file_path1)
            author = request.form.get('author')
            section = request.form.get('sect')
            Cover_art = request.files['image']
            filename2 = secure_filename(Cover_art.filename)
            file_path2 = os.path.join(app.config['UPLOAD_FOLDER'],filename2)
            Cover_art.save(file_path2)
            cred = Section.query.filter_by(name=section).first()
            sec2 = cred.id if cred else None
            ava = 1

            if sec2 is not None: 
                inputs = Book(section_id=sec2, content=file_path1, name=name, author=author, availability=ava,profile=file_path2)
                db.session.add(inputs)
                db.session.commit()
                return redirect(url_for('Abook'))

        sec = Section.query.all()
        return render_template('/add/add_book.html', sec=sec)
    except Exception as e:
        flash("An error occurred: {}".format(str(e)))
        return redirect(url_for('Abook'))


@app.route('/ed/<int:n>',methods=['GET',"POST"])
def Edit_book(n):
    try:
        list1=Book.query.filter_by(id=n).first()
        sec = Section.query.all()
        if request.method == 'POST':
            name = request.form.get('title')
            author = request.form.get('author')
            section = request.form.get('sect')
            print(name)
            print(author)
            print(section)
            content = request.files['location']
            Cover_art = request.files['image']
            cred = Section.query.filter_by(name=section).first()
            sec2 = cred.id if cred else None
            if content and Cover_art:
                filename1 = secure_filename(content.filename)
                file_path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
                content.save(file_path1)
                filename2 = secure_filename(Cover_art.filename)
                file_path2 = os.path.join(app.config['UPLOAD_FOLDER'],filename2)
                Cover_art.save(file_path2)
                list1.content=content
                list1.profile=Cover_art
            list1.name=name
            list1.author=author
            list1.section_id=sec2
            db.session.commit()
            return redirect(url_for('Abook'))

        return render_template('/edit/edit_book.html',list1=list1,sec=sec)
    except Exception as e:
        flash("An error occurred: {}".format(str(e)))
        return redirect(url_for('Abook'))

@app.route('/addsection', methods=["GET", "POST"])
def Add_section():
    try:
        sec = Section.query.all()
        if request.method == "POST":
            des = request.form.get('des')
            name = request.form.get('name')
            t = datetime.datetime.now()
            inputs = Section(date_created=t, description=des, name=name)
            db.session.add(inputs)
            db.session.commit()
            return redirect(url_for('Asection'))

        return render_template('/add/add_section.html', sec=sec)
    except Exception as e:
        flash("An error occurred: {}".format(str(e)))
        return redirect(url_for('Asection'))


@app.route('/edsec/<int:n>',methods=['GET',"POST"])
def Edit_Section(n):
    list1=Section.query.filter_by(id=n).first()
    if request.method == 'POST':
        des = request.form.get('des')
        name = request.form.get('name')
        list1.name=name
        list1.description=des
        db.session.commit()
        return redirect(url_for('Asection'))
    return render_template('edit/edit_section.html',list1=list1)

@app.route('/revoke/<int:n>',methods=["GET","POST"])
def Revoke(n):
    book=Book.query.filter_by(id=n).first()
    ubook=UserBook.query.filter_by(book_id=n).first()
    us=ubook.user_id
    us=User.query.filter_by(id=us).first()
    us.token+=1
    book.availability=1
    db.session.delete(ubook)
    db.session.commit()
    return redirect(url_for('Abook'))

@app.route('/feed',methods=["GET","POST"])
def Feed():
    if request.method == "POST":
        comment=request.form.get('comment')
        feed=request.form.get('feed')
        book=Book.query.filter_by(name=feed).first()
        bid=book.id
        uname=request.form.get('uname')
        uid=User.query.filter_by(username=uname).first()
        uid=uid.id
        rating=request.form.get('rate')
        inputs=Feedback(rating=rating,user_id=uid,book_id=bid,comment=comment)
        db.session.add(inputs)
        db.session.commit()
        return redirect(url_for('Feedbacks',n=uid))
#######################################################  Deleting PARTS HERE ##########################################################

@app.route('/de/<int:book_id>', methods=["GET","POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    try:
        if book.feedbacks:
            for f in book.feedbacks:
                db.session.delete(f)
        u=UserBook.query.filter_by(book_id=book_id).first()
        if u:
            uid=u.user_id
            user=User.query.filter_by(id=uid).first()
            user.token+=1
            db.session.delete(u)
        db.session.delete(book)
        db.session.commit()
        flash("Book deleted successfully.")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the book: {}".format(str(e)))
    return redirect(url_for('Abook'))

@app.route('/dele/<int:section_id>', methods=["GET","POST"])
def delete_section(section_id):
    section = Section.query.filter_by(id=section_id).first()
    try:
        for book in section.books:
            db.session.delete(book)
        db.session.delete(section)
        db.session.commit()
        flash("Section and associated books deleted successfully.")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the section: {}".format(str(e)))
    return redirect(url_for('Asection'))

@app.route('/delete/<int:user_id>', methods=["GET","POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        f=Feedback.query.filter_by(user_id=user_id).first()
        if f:
            db.session.delete(f)
        us = UserBook.query.filter_by(user_id=user_id).all()
        for i in us:
            book_idd = i.book_id
            Bo = Book.query.filter_by(id=book_idd).first()
            Bo.availability+=1
        UserBook.query.filter_by(user_id=user_id).delete()

        db.session.delete(user)
        db.session.commit()
        flash("User and associated records deleted successfully.")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the user: {}".format(str(e)))
    return redirect(url_for('Auser'))


#######################################################  Authentication PARTS HERE ##########################################################
@app.route('/',methods=["GET","POST"])
def Login():
    if request.method == "POST":
        email=request.form.get('email')
        pass1=request.form.get('pass')
        try:
            cred=User.query.filter_by(email=email).first()
            if cred and cred.password == pass1:
                session['user_id'] = cred.id
                return redirect(url_for('Dash', n=cred.id))
            else:
                return render_template('login.html')
        except:
            abort(404)
    return render_template("login.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        Cover_art = request.files['image']
        filename2 = secure_filename(Cover_art.filename)
        file_path2 = os.path.join(app.config['UPLOAD_FOLDER'],filename2)
        Cover_art.save(file_path2)
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            return 'Username already exists!'
        elif existing_email:
            return 'Email already exists!'
        else:
            new_user = User(username=username, email=email, password=password,profile=file_path2)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('Login'))

    return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug = True)