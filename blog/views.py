from flask import render_template, redirect, url_for

from . import app
from .database import session, Entry

PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1, type="Edit", limit=10):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()

    limit = request.args.get('limit', limit)
    limit = int(limit) 
    print(limit)
    if limit < 1 and limit>50:
        limit = PAGINATE_BY
    start = page_index * limit
    end = start + limit

    total_pages = (count - 1) // limit + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )
    
@app.route("/entry/add", methods=["GET"])
def add_entry_get():
    return render_template("add_entry.html")
    
from flask import request, redirect, url_for
from flask.ext.login import current_user, login_required

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/entry/<id>", methods=["GET"])
def show_post(id):
    # show the post with the given id
    entry = session.query(Entry).get(id)
    return render_template("entry.html",
        entry=entry
    )

@app.route("/entry/<id>/edit", methods=["GET"])    
def edit_post(id):
    entry = session.query(Entry).get(id)
    return render_template("edit_entry.html",
        entry=entry
    )

@app.route("/entry/<id>/edit", methods=["POST"])
def edit_entry_post(id):
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    entry2 = session.query(Entry).get(id)
    entry2.title = entry.title
    entry2.content = entry.content
    session.commit()
    return render_template("entry.html",
        entry=entry
    )
    
@app.route("/entry/<id>/delete", methods=["GET"])    
def delete_post(id):
    entry = session.query(Entry).get(id)
    return render_template("delete_entry.html",
        entry=entry
    )

@app.route("/entry/<id>/delete", methods=["POST"])
def delete_entry_post(id):
    print('***entered delete***')
    entry = session.query(Entry).get(id)
    session.delete(entry)
    session.commit()
    return redirect(url_for('index'))
    
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

from flask import flash
from flask.ext.login import login_user
from werkzeug.security import check_password_hash
from .database import User

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))

@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")

    return redirect("/login")

