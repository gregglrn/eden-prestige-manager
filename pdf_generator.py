import os
from math import cos, radians, sin

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


OR = colors.HexColor("#b88a35")
OR_CLAIR = colors.HexColor("#d8bf86")
GRIS = colors.HexColor("#4c4c4c")
GRIS_CLAIR = colors.HexColor("#dddddd")
FOND = colors.HexColor("#fffefd")


class PDFGenerator:
    @staticmethod
    def generer(devis, param=None):
        os.makedirs("pdf", exist_ok=True)
        chemin = os.path.join("pdf", f"{devis.numero}.pdf")

        c = canvas.Canvas(chemin, pagesize=A4)
        largeur, hauteur = A4
        c.setTitle(devis.numero)
        c.setAuthor("EDEN PRESTIGE PAYSAGE")

        PDFGenerator._fond(c, largeur, hauteur)
        PDFGenerator._entete(c, largeur, hauteur, devis, param)
        PDFGenerator._client(c, largeur, hauteur, devis)
        PDFGenerator._tableau(c, largeur, hauteur, devis)
        PDFGenerator._totaux(c, largeur, devis)
        PDFGenerator._bas_de_page(c, largeur, devis)
        PDFGenerator._pied(c, largeur)

        c.showPage()
        c.save()
        return chemin

    @staticmethod
    def _texte(valeur, defaut=""):
        return str(valeur or defaut)

    @staticmethod
    def _argent(valeur):
        return f"{(valeur or 0):,.2f} EUR".replace(",", " ")

    @staticmethod
    def _nombre(valeur):
        if valeur is None:
            return ""
        if float(valeur).is_integer():
            return str(int(valeur))
        return f"{valeur:.2f}".replace(".", ",")

    @staticmethod
    def _ligne_pointillee(c, x1, y, x2):
        c.saveState()
        c.setStrokeColor(GRIS_CLAIR)
        c.setDash(1.1, 2.2)
        c.line(x1, y, x2, y)
        c.restoreState()

    @staticmethod
    def _rectangle(c, x, y, w, h, rayon=4):
        c.saveState()
        c.setStrokeColor(OR_CLAIR)
        c.setLineWidth(0.75)
        c.roundRect(x, y, w, h, rayon, stroke=1, fill=0)
        c.restoreState()

    @staticmethod
    def _fond(c, largeur, hauteur):
        c.setFillColor(FOND)
        c.rect(0, 0, largeur, hauteur, stroke=0, fill=1)
        c.setStrokeColor(OR)
        c.setLineWidth(1)
        c.rect(7 * mm, 7 * mm, largeur - 14 * mm, hauteur - 14 * mm, stroke=1, fill=0)
        PDFGenerator._branche(c, largeur - 28 * mm, hauteur - 57 * mm, 20 * mm, 42)
        PDFGenerator._branche(c, largeur - 43 * mm, hauteur - 118 * mm, 22 * mm, -10)

    @staticmethod
    def _branche(c, x, y, taille, angle):
        c.saveState()
        c.translate(x, y)
        c.rotate(angle)
        c.setStrokeColor(OR)
        c.setFillColor(colors.Color(1, 1, 1, alpha=0))
        c.setLineWidth(0.8)
        c.line(0, 0, taille, taille * 0.9)
        for i in range(5):
            t = (i + 1) / 6
            bx = taille * t
            by = taille * 0.9 * t
            longueur = taille * (0.22 - i * 0.018)
            for cote in (-1, 1):
                c.saveState()
                c.translate(bx, by)
                c.rotate(28 * cote)
                c.ellipse(0, -longueur * 0.14, longueur, longueur * 0.14, stroke=1, fill=0)
                c.restoreState()
        c.restoreState()

    @staticmethod
    def _separateur(c, x, y, w):
        c.saveState()
        c.setStrokeColor(OR_CLAIR)
        c.setLineWidth(0.7)
        c.line(x, y, x + w * 0.42, y)
        c.line(x + w * 0.58, y, x + w, y)
        c.setStrokeColor(OR)
        c.circle(x + w * 0.5, y, 2.3, stroke=1, fill=0)
        c.line(x + w * 0.5, y - 4, x + w * 0.5, y + 4)
        c.restoreState()

    @staticmethod
    def _entete(c, largeur, hauteur, devis, param):
        gauche = 22 * mm
        haut = hauteur - 30 * mm
        milieu = 70 * mm
        droite = 136 * mm

        c.saveState()
        c.setStrokeColor(OR_CLAIR)
        c.line(milieu - 6 * mm, haut - 3 * mm, milieu - 6 * mm, haut - 58 * mm)
        c.restoreState()

        c.setFillColor(OR)
        c.setFont("Times-Bold", 72)
        c.drawCentredString(gauche + 20 * mm, haut - 28 * mm, "E")
        PDFGenerator._branche(c, gauche + 12 * mm, haut - 42 * mm, 15 * mm, -20)
        c.setFont("Times-Bold", 16)
        c.drawCentredString(gauche + 20 * mm, haut - 52 * mm, "EDEN PRESTIGE")
        c.setFont("Times-Bold", 8)
        c.drawCentredString(gauche + 20 * mm, haut - 58 * mm, "PAYSAGE")

        entreprise = PDFGenerator._texte(getattr(param, "entreprise", ""), "EDEN PRESTIGE PAYSAGE")
        c.setFillColor(OR)
        c.setFont("Times-Bold", 12)
        c.drawString(milieu + 3 * mm, haut - 12 * mm, entreprise.upper())
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(milieu + 3 * mm, haut - 20 * mm, "Amenagement & Entretien")
        c.drawString(milieu + 3 * mm, haut - 26 * mm, "de jardins et espaces verts")
        PDFGenerator._separateur(c, milieu + 3 * mm, haut - 36 * mm, 47 * mm)

        infos = [
            ("Telephone", getattr(param, "telephone", "")),
            ("E-mail", getattr(param, "email", "")),
            ("Adresse", " ".join(v for v in [getattr(param, "adresse", ""), getattr(param, "code_postal", ""), getattr(param, "ville", "")] if v)),
        ]
        c.setFont("Helvetica-Bold", 8)
        y = haut - 45 * mm
        for label, valeur in infos:
            c.setFillColor(OR)
            c.circle(milieu + 5 * mm, y + 1.5, 2, stroke=0, fill=1)
            c.setFillColor(GRIS)
            c.drawString(milieu + 12 * mm, y, f"{label} :")
            c.setFont("Helvetica", 8)
            c.drawString(milieu + 30 * mm, y, PDFGenerator._texte(valeur))
            c.setFont("Helvetica-Bold", 8)
            y -= 7 * mm

        c.setFillColor(OR)
        c.setFont("Times-Bold", 26)
        c.drawCentredString(droite + 27 * mm, haut - 25 * mm, "D E V I S")
        PDFGenerator._separateur(c, droite + 2 * mm, haut - 36 * mm, 54 * mm)

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(GRIS)
        lignes = [
            ("Date", devis.date),
            ("No de devis", devis.numero),
            ("Date d'expiration", devis.expiration),
        ]
        y = haut - 43 * mm
        for label, valeur in lignes:
            c.drawString(droite + 2 * mm, y, f"{label} :")
            c.setFont("Helvetica", 8)
            c.drawString(droite + 34 * mm, y, PDFGenerator._texte(valeur))
            c.setFont("Helvetica-Bold", 8)
            y -= 7 * mm

    @staticmethod
    def _client(c, largeur, hauteur, devis):
        x = 20 * mm
        y = hauteur - 126 * mm
        w = largeur - 40 * mm
        h = 31 * mm
        PDFGenerator._rectangle(c, x, y, w, h, 4)

        c.saveState()
        c.setFillColor(colors.HexColor("#fbf7ef"))
        c.setStrokeColor(OR_CLAIR)
        c.roundRect(x, y + h - 12 * mm, 24 * mm, 12 * mm, 4, stroke=1, fill=1)
        c.setFillColor(OR)
        c.setFont("Times-Bold", 10)
        c.drawCentredString(x + 12 * mm, y + h - 8 * mm, "CLIENT")
        c.restoreState()

        client = devis.client_obj
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Bold", 8)
        champs = [
            ("Nom / Societe", client.nom, x + 33 * mm, y + 22 * mm, x + 147 * mm),
            ("Adresse", client.adresse, x + 33 * mm, y + 15 * mm, x + 147 * mm),
            ("Code postal", client.code_postal, x + 33 * mm, y + 8 * mm, x + 76 * mm),
            ("Ville", client.ville, x + 78 * mm, y + 8 * mm, x + 147 * mm),
            ("Telephone", client.telephone, x + 33 * mm, y + 1 * mm, x + 82 * mm),
            ("E-mail", client.email, x + 87 * mm, y + 1 * mm, x + 147 * mm),
        ]
        for label, valeur, sx, sy, ex in champs:
            c.drawString(sx - 24 * mm, sy, f"{label} :")
            c.setFont("Helvetica", 8)
            c.drawString(sx, sy, PDFGenerator._texte(valeur))
            PDFGenerator._ligne_pointillee(c, sx + stringWidth(PDFGenerator._texte(valeur), "Helvetica", 8) + 2, sy - 1, ex)
            c.setFont("Helvetica-Bold", 8)

    @staticmethod
    def _tableau(c, largeur, hauteur, devis):
        x = 20 * mm
        y_top = hauteur - 134 * mm
        w = largeur - 40 * mm
        row_h = 4.3 * mm
        header_h = 7.5 * mm
        colonnes = [0, 14, 88, 106, 127, 153, 177]
        h = header_h + row_h * 20
        y = y_top - h
        PDFGenerator._rectangle(c, x, y, w, h, 3)

        c.setStrokeColor(OR_CLAIR)
        c.setLineWidth(0.55)
        for col in colonnes[1:-1]:
            c.line(x + col * mm, y, x + col * mm, y + h)
        c.line(x, y + h - header_h, x + w, y + h - header_h)

        c.setFillColor(OR)
        c.setFont("Times-Bold", 8)
        titres = ["No", "DESCRIPTION DES PRESTATIONS", "UNITE", "QUANTITE", "PRIX UNITAIRE", "TOTAL"]
        centres = [7, 51, 97, 116.5, 140, 165]
        for titre, centre in zip(titres, centres):
            c.drawCentredString(x + centre * mm, y + h - 5.5 * mm, titre)

        c.setStrokeColor(GRIS_CLAIR)
        c.setLineWidth(0.35)
        for i in range(20):
            yy = y + h - header_h - row_h * (i + 1)
            c.line(x, yy, x + w, yy)

        c.setFillColor(GRIS)
        c.setFont("Helvetica", 6.5)
        lignes = list(devis.lignes)[:20]
        for i in range(20):
            yy = y + h - header_h - row_h * (i + 0.68)
            c.drawCentredString(x + 7 * mm, yy, str(i + 1))
            if i >= len(lignes):
                continue
            ligne = lignes[i]
            c.drawString(x + 17 * mm, yy, PDFGenerator._texte(ligne.designation)[:56])
            c.drawCentredString(x + 97 * mm, yy, PDFGenerator._texte(ligne.unite))
            c.drawRightString(x + 124 * mm, yy, PDFGenerator._nombre(ligne.quantite))
            c.drawRightString(x + 150 * mm, yy, PDFGenerator._argent(ligne.prix))
            c.drawRightString(x + 174 * mm, yy, PDFGenerator._argent(ligne.total))

    @staticmethod
    def _totaux(c, largeur, devis):
        x = largeur - 82 * mm
        y = 52 * mm
        w = 62 * mm
        h = 18 * mm
        PDFGenerator._rectangle(c, x, y, w, h, 3)
        c.setStrokeColor(OR_CLAIR)
        c.line(x + 34 * mm, y, x + 34 * mm, y + h)
        c.line(x, y + 9 * mm, x + w, y + 9 * mm)
        c.setFillColor(OR)
        c.setFont("Times-Bold", 9)
        c.drawCentredString(x + 17 * mm, y + 12.2 * mm, "RABAIS")
        c.drawCentredString(x + 17 * mm, y + 3.2 * mm, "TOTAL")
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x + w - 4 * mm, y + 12.2 * mm, PDFGenerator._argent(devis.remise))
        c.drawRightString(x + w - 4 * mm, y + 3.2 * mm, PDFGenerator._argent(devis.total))

    @staticmethod
    def _bas_de_page(c, largeur, devis):
        y = 20 * mm
        h = 30 * mm
        marge = 20 * mm
        gap = 3 * mm
        w1 = 56 * mm
        w2 = 51 * mm
        w3 = largeur - 2 * marge - w1 - w2 - 2 * gap
        blocs = [(marge, w1), (marge + w1 + gap, w2), (marge + w1 + w2 + 2 * gap, w3)]

        titres = ["CONDITIONS DE PAIEMENT", "CONDITIONS GENERALES", "BON POUR ACCORD"]
        for index, (x, w) in enumerate(blocs):
            PDFGenerator._rectangle(c, x, y, w, h, 4)
            c.setFillColor(OR)
            c.setFont("Times-Bold", 8)
            c.drawCentredString(x + w / 2, y + h - 9 * mm, titres[index])

        c.setFillColor(GRIS)
        c.setFont("Helvetica", 6.8)
        c.drawString(blocs[0][0] + 4 * mm, y + 15 * mm, "Modalites de paiement :")
        c.line(blocs[0][0] + 34 * mm, y + 14.6 * mm, blocs[0][0] + blocs[0][1] - 4 * mm, y + 14.6 * mm)
        c.drawString(blocs[0][0] + 4 * mm, y + 7 * mm, "Echeance :")
        c.line(blocs[0][0] + 20 * mm, y + 6.6 * mm, blocs[0][0] + blocs[0][1] - 4 * mm, y + 6.6 * mm)

        texte = [
            "Ce devis est valable pour une duree",
            "de 30 jours a compter de sa date d'emission.",
            "Toute modification pourra faire",
            "l'objet d'un avenant.",
        ]
        for i, ligne in enumerate(texte):
            c.drawString(blocs[1][0] + 4 * mm, y + 16 * mm - i * 4.1 * mm, ligne)

        x3, w3 = blocs[2]
        c.drawString(x3 + 4 * mm, y + 16 * mm, "Fait a :")
        c.line(x3 + 15 * mm, y + 15.6 * mm, x3 + 38 * mm, y + 15.6 * mm)
        c.drawString(x3 + 44 * mm, y + 16 * mm, "Le :")
        c.drawString(x3 + 53 * mm, y + 22 * mm, "____ / ____ / ______")
        c.drawString(x3 + 4 * mm, y + 9 * mm, "Signature et cachet (precedes de la mention")
        c.drawString(x3 + 4 * mm, y + 5 * mm, "Bon pour accord) :")
        PDFGenerator._rectangle(c, x3 + 4 * mm, y + 3 * mm, w3 - 8 * mm, 5 * mm, 2)

    @staticmethod
    def _pied(c, largeur):
        y = 13 * mm
        PDFGenerator._separateur(c, 73 * mm, y + 4 * mm, 64 * mm)
        c.setFillColor(OR)
        c.setFont("Times-Italic", 16)
        c.drawCentredString(largeur / 2, y - 2 * mm, "Merci pour votre confiance")
        c.setFont("Times-Bold", 8)
        c.drawCentredString(largeur / 2, y - 6 * mm, "E D E N   P R E S T I G E   P A Y S A G E")

