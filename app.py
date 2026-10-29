from dataclasses import asdict
from flask import Flask, abort, jsonify, render_template, request

import catalog as c

app = Flask(__name__)


@app.context_processor
def inject_globals():
    return dict(STYLES=c.STYLES, CATEGORIES=c.CATEGORIES, BUDGETS=c.BUDGETS)


# ------------------------------------------------------------ pages
@app.get("/")
def discover():
    q = request.args.get("q", "")
    category = request.args.get("category", "")
    styles = request.args.getlist("style")
    budgets = request.args.getlist("budget")
    items = c.filter_items(q, category, styles, budgets)
    filtered = bool(q or category or styles or budgets)
    return render_template("discover.html", items=items, q=q, category=category,
                           sel_styles=styles, sel_budgets=budgets, filtered=filtered)


@app.get("/item/<item_id>")
def item_detail(item_id):
    item = c.BY_ID.get(item_id) or abort(404)
    return render_template("detail.html", item=item)


@app.get("/designer")
def designer():
    return render_template("designer.html")


@app.get("/rooms")
def rooms():
    return render_template("rooms.html")


@app.get("/quiz")
def quiz():
    return render_template("quiz.html")


@app.get("/style")
def style_page():
    return render_template("style.html")


# ------------------------------------------------------------ API
@app.get("/api/catalog")
def api_catalog():
    return jsonify([asdict(i) for i in c.CATALOG])


@app.get("/api/recommend")
def api_recommend():
    items = c.recommend(request.args.get("primary", ""), request.args.get("secondary", ""),
                        request.args.get("budget", ""))
    return jsonify([asdict(i) for i in items])


@app.get("/api/quiz")
def api_quiz_questions():
    return jsonify(c.QUIZ)


@app.post("/api/quiz")
def api_quiz_submit():
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", [])
    try:
        if len(answers) != len(c.QUIZ):
            raise ValueError("answer every question")
        profile = c.build_profile(answers)
    except (ValueError, IndexError, TypeError) as e:
        return jsonify(error=str(e)), 400
    return jsonify(profile)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
