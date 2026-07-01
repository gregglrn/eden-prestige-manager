from flask import Flask, send_file
from flask import render_template
from flask import request
from flask import redirect
from flask import jsonify
from models import Devis
from config import Config
from database import db
from datetime import datetime
from models import Client, Devis, LigneDevis
from pdf_generator import PDFGenerator
from models import Prestation

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/devis", methods=["POST"])
def devis():

    # Recherche du client
    client = Client.query.filter_by(
        nom=request.form["nom"]
    ).first()

    # Création du client s'il n'existe pas
    if client is None:

        client = Client(
            nom=request.form["nom"],
            adresse=request.form["adresse_client"],
            code_postal=request.form["cp"],
            ville=request.form["ville"],
            telephone=request.form["telephone"],
            email=request.form["mail"]
        )

        db.session.add(client)
        db.session.commit()

    # Numéro automatique
    annee = datetime.now().year

    dernier = Devis.query.order_by(
        Devis.id.desc()
    ).first()

    if dernier:
        numero = int(dernier.numero.split("-")[-1]) + 1
    else:
        numero = 1

    numero_devis = f"DEV-{annee}-{numero:04d}"

    devis = Devis(

        numero=numero_devis,

        date=datetime.now().strftime("%d/%m/%Y"),

        expiration="",

        remise=0,

        total=0,

        client_id=client.id,

    )

    db.session.add(devis)

    db.session.commit()

    total = 0

    designations = request.form.getlist("designation[]")
    unites = request.form.getlist("unite[]")
    quantites = request.form.getlist("quantite[]")
    prix = request.form.getlist("prix[]")
    prestation_ids = request.form.getlist("prestation_id[]")

    for i in range(len(designations)):
        qte = float(quantites[i])
        pu = float(prix[i])

        prestation_id = None
        if prestation_ids[i]:
            prestation_id = int(prestation_ids[i])

        ligne = LigneDevis(
            designation=designations[i],
            unite=unites[i],
            quantite=qte,
            prix=pu,
            total=qte * pu,
            prestation_id=prestation_id,
            devis_id=devis.id
        )

        total += qte * pu
        db.session.add(ligne)

    devis.total = total
    db.session.commit()

    return redirect(f"/devis/{devis.id}")

@app.route("/")

def accueil():

    return render_template("index.html")

@app.route("/clients")
def clients():

    liste = Client.query.order_by(Client.nom).all()

    return render_template(
        "clients.html",
        clients=liste
    )


@app.route("/ajouter_client", methods=["POST"])
def ajouter_client():

    client = Client(

        nom=request.form["nom"],

        adresse=request.form["adresse"],

        code_postal=request.form["cp"],

        ville=request.form["ville"],

        telephone=request.form["telephone"],

        email=request.form["email"]

    )

    db.session.add(client)

    db.session.commit()

    return redirect("/clients")

@app.route("/api/clients")
def api_clients():

    clients = Client.query.order_by(Client.nom).all()

    resultat = []

    for c in clients:

        resultat.append({

            "id": c.id,
            "nom": c.nom,
            "adresse": c.adresse,
            "cp": c.code_postal,
            "ville": c.ville,
            "telephone": c.telephone,
            "email": c.email

        })

    return jsonify(resultat)

@app.route("/historique")
def historique():

    devis = Devis.query.order_by(
        Devis.id.desc()
    ).all()

    return render_template(
        "historique.html",
        devis=devis
    )

@app.route("/devis/<int:id>")
def voir_devis(id):

    devis = Devis.query.get_or_404(id)

    return render_template(
        "apercu.html",
        devis=devis
    )

@app.route("/pdf/<int:id>")
def pdf(id):

    devis = Devis.query.get_or_404(id)

    chemin = PDFGenerator.generer(devis)

    return send_file (
        chemin,
        as_attachment=False
    )

@app.route("/prestations")
def prestations():

    prestations = Prestation.query.order_by(
        Prestation.designation
    ).all()

    return render_template(
        "prestations.html",
        prestations=prestations
    )

@app.route("/ajouter_prestation",methods=["POST"])
def ajouter_prestation():

    prestation = Prestation(

        designation=request.form["designation"],

        unite=request.form["unite"],

        prix=float(request.form["prix"])

    )

    db.session.add(prestation)

    db.session.commit()

    return redirect("/prestations")

@app.route("/api/prestations")
def api_prestations():

    prestations = Prestation.query.order_by(
        Prestation.designation
    ).all()

    return jsonify([
        {
            "id": p.id,
            "designation": p.designation,
            "unite": p.unite,
            "prix": p.prix
        }
        for p in prestations
    ])

if __name__ == "__main__":

    app.run(debug=True)