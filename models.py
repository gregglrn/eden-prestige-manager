from database import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.String(150), nullable=False)
    adresse = db.Column(db.String(255))
    code_postal = db.Column(db.String(10))
    ville = db.Column(db.String(100))
    telephone = db.Column(db.String(30))
    email = db.Column(db.String(150))

    devis = db.relationship("Devis", backref="client_obj", lazy=True)

    def __repr__(self):
        return f"<Client {self.nom}>"



class Devis(db.Model):
    __tablename__ = "devis"

    id = db.Column(db.Integer, primary_key=True)

    numero = db.Column(db.String(20), unique=True)

    date = db.Column(db.String(20))

    expiration = db.Column(db.String(20))

    remise = db.Column(db.Float, default=0)

    total = db.Column(db.Float, default=0)

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id")
    )

    lignes = db.relationship(
        "LigneDevis",
        backref="devis",
        cascade="all, delete",
        lazy=True
    )



class LigneDevis(db.Model):
    __tablename__ = "lignes_devis"

    id = db.Column(db.Integer, primary_key=True)

    designation = db.Column(db.String(255))

    unite = db.Column(db.String(30))

    quantite = db.Column(db.Float)

    prix = db.Column(db.Float)

    total = db.Column(db.Float)

    devis_id = db.Column(
        db.Integer,
        db.ForeignKey("devis.id")
    )

    prestation_id = db.Column(
    db.Integer,
    db.ForeignKey("prestations.id"),
    nullable=True
)

prestation = db.relationship("Prestation")


class Prestation(db.Model):
    __tablename__ = "prestations"

    id = db.Column(db.Integer, primary_key=True)

    designation = db.Column(db.String(150), nullable=False)

    unite = db.Column(db.String(50))

    prix = db.Column(db.Float)

    def __repr__(self):
        return f"<Prestation {self.designation}>"