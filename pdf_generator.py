from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os


class PDFGenerator:

    @staticmethod
    def generer(devis):

        if not os.path.exists("pdf"):
            os.makedirs("pdf")

        chemin = f"pdf/{devis.numero}.pdf"

        c = canvas.Canvas(chemin, pagesize=A4)

        largeur, hauteur = A4

        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, hauteur-60, "DEVIS")

        c.setFont("Helvetica", 12)

        c.drawString(50, hauteur-100, f"N° {devis.numero}")

        c.drawString(50, hauteur-120, f"Date : {devis.date}")

        c.drawString(50, hauteur-160, "CLIENT")

        c.drawString(50, hauteur-180, devis.client_obj.nom)

        c.drawString(50, hauteur-200, devis.client_obj.adresse)

        c.drawString(
            50,
            hauteur-220,
            f"{devis.client_obj.code_postal} {devis.client_obj.ville}"
        )

        y = hauteur-280

        c.setFont("Helvetica-Bold",12)

        c.drawString(50,y,"Désignation")

        c.drawString(300,y,"Qté")

        c.drawString(360,y,"PU")

        c.drawString(450,y,"Total")

        y -= 25

        c.setFont("Helvetica",11)

        for ligne in devis.lignes:

            c.drawString(50,y,ligne.designation)

            c.drawString(310,y,str(ligne.quantite))

            c.drawString(360,y,f"{ligne.prix:.2f}")

            c.drawString(450,y,f"{ligne.total:.2f}")

            y-=20

        c.setFont("Helvetica-Bold",14)

        c.drawString(360,80,"TOTAL")

        c.drawString(450,80,f"{devis.total:.2f} €")

        c.save()

        return chemin