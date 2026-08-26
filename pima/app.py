from flask import Flask, jsonify, render_template, redirect, url_for


app = Flask(__name__)

@app.route('/')
def index():
    return "welcome to our site"

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/user/<name>')
def user(name):
    return f"welcome {name}!!"

@app.route("/post/<int:post_id>")
def show_post(post_id):
    return f"post id:{post_id}.."

@app.route("/contact")
def contact():
    return "U can contact via 9342531156"

@app.route("/new-home")
def new_home():
    return redirect(url_for("home"))

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
        "error": "page not found",
        "message": "the requested url not found"
    }),404

@app.errorhandler(500)
def internal(e):
    return f"an internal server error  happenned try later",500



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5001)
