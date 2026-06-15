from flask import Flask, render_template
from ucetnictvi.routes import ucetnictvi_bp
from dane.routes import dane_bp
from nsn.routes import nsn_bp
from scitani.routes import scitani_bp
from odcitani.routes import odcitani_bp
from restaurace.routes import restaurace_bp
from rovnice.routes import rovnice_bp
from rovnicejmenovatel.routes import rovnicejmenovatel_bp
from soustava.routes import soustava_bp
from ucitel.routes import ucitel_bp
from algebra.routes import algebra_bp
from intervaly.routes import intervaly_bp
from nerovnice.routes import nerovnice_bp


app = Flask(__name__)
app.secret_key = "tajny_klic"

app.register_blueprint(ucetnictvi_bp, url_prefix="/ucetnictvi")
app.register_blueprint(dane_bp, url_prefix="/dane")
app.register_blueprint(nsn_bp, url_prefix="/nsn")
app.register_blueprint(scitani_bp, url_prefix="/scitani")
app.register_blueprint(odcitani_bp, url_prefix="/odcitani")
app.register_blueprint(restaurace_bp, url_prefix="/restaurace")
app.register_blueprint(rovnice_bp, url_prefix="/rovnice")
app.register_blueprint(rovnicejmenovatel_bp, url_prefix="/rovnicejmenovatel")
app.register_blueprint(soustava_bp, url_prefix="/soustava")
app.register_blueprint(ucitel_bp, url_prefix="/ucitel")
app.register_blueprint(algebra_bp, url_prefix="/algebra")
app.register_blueprint(intervaly_bp, url_prefix="/intervaly")
app.register_blueprint(nerovnice_bp, url_prefix="/nerovnice")


@app.route("/")
def menu():
    return render_template("menu.html")

if __name__ == "__main__":
    app.run(debug=True)
