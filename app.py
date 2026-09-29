"""Web interface (Flask) for the Digital Library Management System.

Run:  python app.py   then open  http://localhost:5000
"""
from flask import Flask, render_template, request, redirect, url_for, flash, g
from library import Library, LOAN_DAYS, FINE_PER_DAY

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # needed for flash messages


def get_lib():
    # A new connection per request keeps SQLite safe with Flask's threads.
    if "lib" not in g:
        g.lib = Library()
    return g.lib


@app.teardown_appcontext
def close_lib(_exc):
    lib = g.pop("lib", None)
    if lib:
        lib.close()


def run(action, success_msg):
    """Run an action, flash success or the error message, go back home."""
    try:
        result = action()
        flash(success_msg(result) if callable(success_msg) else success_msg, "ok")
    except ValueError as err:
        flash(str(err), "error")
    return redirect(url_for("index"))


@app.route("/")
def index():
    lib = get_lib()
    q = request.args.get("q", "").strip()
    books = lib.search_books(q) if q else lib.list_books()
    return render_template(
        "index.html",
        books=books,
        members=lib.list_members(),
        active_loans=lib.list_loans(active_only=True),
        history=lib.list_loans(active_only=False),
        q=q, loan_days=LOAN_DAYS, fine=FINE_PER_DAY,
    )


@app.post("/books/add")
def add_book():
    f = request.form
    return run(
        lambda: get_lib().add_book(
            f["title"], f["author"], f["isbn"], int(f.get("copies") or 1)
        ),
        "Book added.",
    )


@app.post("/books/<int:book_id>/remove")
def remove_book(book_id):
    return run(lambda: get_lib().remove_book(book_id), "Book removed.")


@app.post("/members/add")
def add_member():
    f = request.form
    return run(lambda: get_lib().add_member(f["name"], f["email"]), "Member registered.")


@app.post("/loans/issue")
def issue():
    f = request.form
    return run(
        lambda: get_lib().issue_book(int(f["book_id"]), int(f["member_id"])),
        lambda r: f"Book issued. Due on {r[1]}.",
    )


@app.post("/loans/<int:loan_id>/return")
def return_book(loan_id):
    return run(
        lambda: get_lib().return_book(loan_id),
        lambda fine: f"Book returned. Late fine: {fine}." if fine else "Book returned. No fine.",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
