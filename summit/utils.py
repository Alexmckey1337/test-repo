# -*- coding: utf-8
from __future__ import unicode_literals

import os
from io import BytesIO

from django.conf import settings
from django.shortcuts import get_object_or_404
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from summit.models import SummitAnket


def generate_ticket(code):
    if code != '00000000':
        anket = get_object_or_404(SummitAnket, code=code)
        user = anket.user
        first_name = user.first_name
        last_name = user.last_name
    else:
        first_name = 'No_name'
        last_name = 'No_name'

    logo = os.path.join(settings.MEDIA_ROOT, 'ticket.jpg')

    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    w = .035 * A4[0] * cm
    v = .035 * A4[1] * cm - w * 941 / 2241

    try:
        c.drawImage(logo, 0, v, width=w, height=w * 941 / 2241)
    except OSError:
        pass
    c.setFont('FreeSans', 46 * w / 2241)
    c.drawString(80 * w / 2241, 165 * w / 2241 + v, first_name)
    c.drawString(970 * w / 2241, 165 * w / 2241 + v, last_name)

    barcode_font_size = 70 * w / 2241
    barcode = createBarcodeDrawing('Code128', value=code, lquiet=0,
                                   barWidth=1.65, barHeight=465 / 2 * w / 2241,
                                   humanReadable=True,
                                   fontSize=barcode_font_size, fontName='FreeSans')

    drawing_width = 988 / 2 * w / 2241
    barcode_scale = drawing_width / barcode.width
    drawing_height = barcode.height * barcode_scale

    drawing = Drawing(drawing_width, drawing_height)
    drawing.scale(barcode_scale, barcode_scale)
    drawing.add(barcode, name='barcode')

    drawing_rotated = Drawing(drawing_height, drawing_width)
    drawing_rotated.rotate(90)
    drawing_rotated.translate(0, -drawing_height)
    drawing_rotated.add(drawing, name='drawing')
    renderPDF.draw(drawing_rotated, c, 1974 * w / 2241, 200 * w / 2241 + v)

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()

    return pdf
