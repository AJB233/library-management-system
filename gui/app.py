from __future__ import annotations

from typing import Optional

from flask import Flask, render_template, request, redirect, url_for, flash

from backend import library_service

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # for flash messages; in real app, use env


@app.route("/")
def index():
    return redirect(url_for("search"))


# ----------------------------
# Book search + checkout
# ----------------------------

@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.args.get("q", "").strip()
    results = []

    if query:
        results = library_service.search_books(query)

    return render_template("search.html", query=query, results=results)


@app.route("/checkout", methods=["POST"])
def checkout():
    isbn = request.form.get("isbn", "").strip()
    card_id = request.form.get("card_id", "").strip()

    if not isbn or not card_id:
        flash("ISBN and Card ID are required for checkout.", "error")
        return redirect(url_for("search", q=isbn))

    success, msg = library_service.checkout_book(isbn, card_id)
    flash(msg, "success" if success else "error")
    return redirect(url_for("search", q=isbn))


# ----------------------------
# Borrower dashboard
# ----------------------------

@app.route("/borrower", methods=["GET", "POST"])
def borrower():
    card_id: Optional[str] = None
    borrower = None
    loans = []
    fines = []

    if request.method == "POST":
        card_id = request.form.get("card_id", "").strip()
        return redirect(url_for("borrower", card_id=card_id))

    card_id = request.args.get("card_id", "").strip()
    if card_id:
        borrower = library_service.get_borrower(card_id)
        loans = library_service.get_borrower_loans(card_id, include_history=True)
        fines = library_service.get_borrower_fines(card_id, only_unpaid=False)

    return render_template(
        "borrower.html",
        card_id=card_id,
        borrower=borrower,
        loans=loans,
        fines=fines,
    )


@app.route("/checkin", methods=["POST"])
def checkin():
    loan_id = request.form.get("loan_id", "").strip()
    card_id = request.form.get("card_id", "").strip()

    if not loan_id.isdigit():
        flash("Loan ID must be an integer.", "error")
        return redirect(url_for("borrower", card_id=card_id))

    success, msg = library_service.checkin_book(int(loan_id))
    flash(msg, "success" if success else "error")
    return redirect(url_for("borrower", card_id=card_id))


@app.route("/pay_fine", methods=["POST"])
def pay_fine():
    loan_id = request.form.get("loan_id", "").strip()
    card_id = request.form.get("card_id", "").strip()

    if not loan_id.isdigit():
        flash("Loan ID must be an integer.", "error")
        return redirect(url_for("borrower", card_id=card_id))

    success, msg = library_service.pay_fine(int(loan_id))
    flash(msg, "success" if success else "error")
    return redirect(url_for("borrower", card_id=card_id))


if __name__ == "__main__":
    # Run with: python -m gui.app
    app.run(debug=True)
