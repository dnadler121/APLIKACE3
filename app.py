from flask import Flask, render_template
from matematika.routes import matematika_bp
from ucetnictvi.routes import ucetnictvi_bp
from dane.routes import dane_bp
from nsn.routes import nsn_bp
from scitani.routes import scitani_bp
from odcitani.routes import odcitani_bp

app = Flask(__name__)
app.secret_key = "tajny_klic"

app.register_blueprint(matematika_bp, url_prefix="/matematika")
app.register_blueprint(ucetnictvi_bp, url_prefix="/ucetnictvi")
app.register_blueprint(dane_bp, url_prefix="/dane")
app.register_blueprint(nsn_bp, url_prefix="/nsn")
app.register_blueprint(scitani_bp, url_prefix="/scitani")
app.register_blueprint(odcitani_bp, url_prefix="/odcitani")

@app.route("/")
def menu():
    return render_template("menu.html")

if __name__ == "__main__":
    app.run(debug=True)