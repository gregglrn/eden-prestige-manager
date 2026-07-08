import os
from datetime import datetime

from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, url_for
from sqlalchemy import inspect
from werkzeug.utils import secure_filename

from config import Config
from database import db
from models import Client, Devis, LigneDevis, Parametres, Prestation
from pdf_generator import PDFGenerator


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


with app.app_context():
    db.create_all()
    colonnes = [colonne["name"] for colonne in inspect(db.engine).get_columns("devis")]
    if "objet" not in colonnes:
        with db.engine.connect() as connection:
            connection.exec_driver_sql("ALTER TABLE devis ADD COLUMN objet VARCHAR(255)")
            connection.commit()


def convertir_nombre(valeur, defaut=0):
    try:
        return float(str(valeur).replace(",", "."))
    except (TypeError, ValueError):
        return defaut


def prochain_numero_devis():
    annee = datetime.now().year
    dernier = Devis.query.order_by(Devis.id.desc()).first()
    if not dernier or not dernier.numero:
        compteur = 1
    else:
        try:
            compteur = int(dernier.numero.split("-")[-1]) + 1
        except ValueError:
            compteur = dernier.id + 1
    return f"DEV-{annee}-{compteur:04d}"


def obtenir_parametres():
    param = Parametres.query.first()
    if param is None:
        param = Parametres(entreprise="EDEN PRESTIGE PAYSAGE")
        db.session.add(param)
        db.session.commit()
    return param


def enregistrer_lignes(devis):
    LigneDevis.query.filter_by(devis_id=devis.id).delete()
    total_brut = 0

    designations = request.form.getlist("designation[]")
    unites = request.form.getlist("unite[]")
    quantites = request.form.getlist("quantite[]")
    prix = request.form.getlist("prix[]")
    prestation_ids = request.form.getlist("prestation_id[]")

    for index, designation in enumerate(designations):
        designation = designation.strip()
        if not designation:
            continue

        quantite = convertir_nombre(quantites[index] if index < len(quantites) else 0)
        prix_unitaire = convertir_nombre(prix[index] if index < len(prix) else 0)
        unite = unites[index] if index < len(unites) else ""
        prestation_id = None

        if index < len(prestation_ids) and prestation_ids[index]:
            prestation_id = int(prestation_ids[index])

        total_ligne = quantite * prix_unitaire
        total_brut += total_ligne
        db.session.add(
            LigneDevis(
                designation=designation,
                unite=unite,
                quantite=quantite,
                prix=prix_unitaire,
                total=total_ligne,
                prestation_id=prestation_id,
                devis_id=devis.id,
            )
        )

    devis.remise = convertir_nombre(request.form.get("remise"))
    devis.total = max(total_brut - devis.remise, 0)


@app.route("/")
def accueil():
    return render_template(
        "index.html",
        clients=Client.query.order_by(Client.nom).all(),
        prestations=Prestation.query.order_by(Prestation.designation).all(),
        param=obtenir_parametres(),
        prochain_numero=prochain_numero_devis(),
    )


@app.route("/devis", methods=["POST"])
def devis():
    client = Client.query.filter_by(nom=request.form["nom"]).first()
    if client is None:
        client = Client(
            nom=request.form["nom"],
            adresse=request.form["adresse_client"],
            code_postal=request.form["cp"],
            ville=request.form["ville"],
            telephone=request.form["telephone"],
            email=request.form["mail"],
        )
        db.session.add(client)
        db.session.commit()

    nouveau_devis = Devis(
        numero=prochain_numero_devis(),
        date=datetime.now().strftime("%d/%m/%Y"),
        expiration=request.form.get("expiration", ""),
        objet=request.form.get("objet", ""),
        remise=0,
        total=0,
        client_id=client.id,
    )
    db.session.add(nouveau_devis)
    db.session.commit()
    enregistrer_lignes(nouveau_devis)
    db.session.commit()
    return redirect(url_for("voir_devis", id=nouveau_devis.id))


@app.route("/clients")
def clients():
    return render_template("clients.html", clients=Client.query.order_by(Client.nom).all())


@app.route("/ajouter_client", methods=["POST"])
def ajouter_client():
    db.session.add(
        Client(
            nom=request.form["nom"],
            adresse=request.form["adresse"],
            code_postal=request.form["cp"],
            ville=request.form["ville"],
            telephone=request.form["telephone"],
            email=request.form["email"],
        )
    )
    db.session.commit()
    return redirect(url_for("clients"))


@app.route("/api/clients")
def api_clients():
    return jsonify([
        {
            "id": client.id,
            "nom": client.nom,
            "adresse": client.adresse or "",
            "cp": client.code_postal or "",
            "ville": client.ville or "",
            "telephone": client.telephone or "",
            "email": client.email or "",
        }
        for client in Client.query.order_by(Client.nom).all()
    ])


@app.route("/historique")
def historique():
    return render_template("historique.html", devis=Devis.query.order_by(Devis.id.desc()).all())


@app.route("/devis/<int:id>")
def voir_devis(id):
    return render_template("apercu.html", devis=Devis.query.get_or_404(id))


@app.route("/pdf/<int:id>")
def pdf(id):
    chemin = PDFGenerator.generer(Devis.query.get_or_404(id), obtenir_parametres())
    return send_file(chemin, as_attachment=False)


@app.route("/prestations")
def prestations():
    return render_template("prestations.html", prestations=Prestation.query.order_by(Prestation.designation).all())


@app.route("/ajouter_prestation", methods=["POST"])
def ajouter_prestation():
    db.session.add(
        Prestation(
            designation=request.form["designation"],
            unite=request.form["unite"],
            prix=convertir_nombre(request.form["prix"]),
        )
    )
    db.session.commit()
    return redirect(url_for("prestations"))


@app.route("/api/prestations")
def api_prestations():
    return jsonify([
        {
            "id": prestation.id,
            "designation": prestation.designation,
            "unite": prestation.unite or "",
            "prix": prestation.prix or 0,
            "texte": f"{prestation.designation} - {prestation.unite or ''} - {(prestation.prix or 0):.2f} EUR",
        }
        for prestation in Prestation.query.order_by(Prestation.designation).all()
    ])


@app.route("/parametres")
def parametres():
    return render_template("parametres.html", param=obtenir_parametres())


@app.route("/parametres", methods=["POST"])
def enregistrer_parametres():
    param = obtenir_parametres()
    param.entreprise = request.form["entreprise"]
    param.adresse = request.form["adresse"]
    param.code_postal = request.form["code_postal"]
    param.ville = request.form["ville"]
    param.telephone = request.form["telephone"]
    param.email = request.form["email"]
    param.siret = request.form["siret"]
    param.tva = request.form["tva"]
    param.iban = request.form["iban"]
    param.bic = request.form["bic"]
    param.site = request.form["site"]

    logo = request.files.get("logo")
    if logo and logo.filename:
        filename = secure_filename(logo.filename)
        dossier_logos = os.path.join(app.static_folder, "logos")
        os.makedirs(dossier_logos, exist_ok=True)
        logo.save(os.path.join(dossier_logos, filename))
        param.logo = filename

    db.session.commit()
    flash("Parametres enregistres avec succes.", "success")
    return redirect(url_for("parametres"))


@app.route("/devis/<int:id>/modifier")
def modifier_devis(id):
    devis_a_modifier = Devis.query.get_or_404(id)
    return render_template(
        "index.html",
        devis=devis_a_modifier,
        clients=Client.query.order_by(Client.nom).all(),
        prestations=Prestation.query.order_by(Prestation.designation).all(),
        param=obtenir_parametres(),
        prochain_numero=devis_a_modifier.numero,
        mode="edition",
    )


@app.route("/devis/<int:id>/mettre-a-jour", methods=["POST"])
def mettre_a_jour_devis(id):
    devis_a_modifier = Devis.query.get_or_404(id)
    client = devis_a_modifier.client_obj
    client.nom = request.form["nom"]
    client.adresse = request.form["adresse_client"]
    client.code_postal = request.form["cp"]
    client.ville = request.form["ville"]
    client.telephone = request.form["telephone"]
    client.email = request.form["mail"]

    devis_a_modifier.expiration = request.form.get("expiration", "")
    devis_a_modifier.objet = request.form.get("objet", "")
    enregistrer_lignes(devis_a_modifier)
    db.session.commit()
    flash("Devis modifie avec succes.", "success")
    return redirect(url_for("historique"))


@app.route("/devis/<int:id>/supprimer")
def supprimer_devis(id):
    devis_a_supprimer = Devis.query.get_or_404(id)
    db.session.delete(devis_a_supprimer)
    db.session.commit()
    return redirect(url_for("historique"))


if __name__ == "__main__":
    app.run(debug=True)
