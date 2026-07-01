from flask import render_template
from weasyprint import HTML

class DevisGenerator:

    @staticmethod
    def generer(devis):

        html = render_template(
            "devis_pdf.html",
            devis=devis
        )

        HTML(string=html).write_pdf(
            f"pdf/{devis.numero}.pdf"
        )