# -*- coding: utf-8
from __future__ import unicode_literals

import os
from io import BytesIO

from django.conf import settings
from django.shortcuts import get_object_or_404
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw

from summit.models import SummitAnket, Summit


def generate_ticket(code):
    if code != '00000000':
        anket = get_object_or_404(SummitAnket, code=code)
        user = anket.user
        photo = user.image
    else:
        user = None
        photo = None

    logo = os.path.join(settings.MEDIA_ROOT, 'background.png')

    buffer = BytesIO()

    w = 90 * mm
    h = 58 * mm
    c = canvas.Canvas(buffer, pagesize=(w, h))
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansBold', 'FreeSansBold.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansIt', 'FreeSansOblique.ttf'))

    create_ticket_page(c, code, logo, photo, w, h, user)
    c.save()
    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_ticket_by_summit(summit_id):
    logo = os.path.join(settings.MEDIA_ROOT, 'background.png')

    buffer = BytesIO()

    w = 90 * mm
    h = 58 * mm
    c = canvas.Canvas(buffer, pagesize=(w, h))
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansBold', 'FreeSansBold.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansIt', 'FreeSansOblique.ttf'))

    summit = Summit.objects.get(id=summit_id)
    ankets = summit.ankets.all()
    """
    SELECT u1.user_ptr_id, u2.* FROM account_customuser u1
      INNER JOIN account_customuser u2 on u1.lft > u2.lft and u1.rght < u2.rght and u1.tree_id = u2.tree_id
      INNER JOIN hierarchy_hierarchy h on u2.hierarchy_id = h.id
    WHERE u1.hierarchy_id = 2 and h.level in (4, 2)
    ORDER BY u2.level;
    """
    for anket in ankets[:100]:
        create_ticket_page(c, anket.code, logo, anket.user.image, w, h, anket.user)
    c.save()
    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def to_circle(im):
    circle = Image.new('L', im.size, 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, im.size[0], im.size[1]), fill=255)
    im.putalpha(circle)
    return im


def create_ticket_page(c, code, logo, photo, w, h, user):
    try:
        c.drawImage(logo, (w - 51 * mm) / 2, (h - 51 * mm) / 2, width=51 * mm, height=51 * mm, mask='auto')
    except OSError:
        pass
    try:
        if photo is not None:

            im = Image.open(os.path.join(settings.MEDIA_ROOT, photo.path))
            im = to_circle(im)
            ir = ImageReader(im)
            c.drawImage(ir, 7 * mm, 31 * mm, width=20 * mm, height=20 * mm, mask='auto')
    except ValueError:
        pass
    except OSError:
        pass
    c.setFillColor(HexColor('0x3f4e55'))
    c.setFont('FreeSansBold', 126 * w / 2241)
    c.drawString(750 * w / 2241, 925 * w / 2241, user.last_name if user else 'No name')
    c.drawString(750 * w / 2241, 775 * w / 2241, user.first_name if user else 'No name')
    c.setFillColor(HexColor('0x66787f'))

    c.setFont('FreeSansIt', 51 * w / 2241)
    if user and user.get_pastor():
        c.drawString(450 * w / 2241, 485 * w / 2241, '(пастор)')
    if user and user.get_bishop():
        c.drawString(450 * w / 2241, 335 * w / 2241, '(епископ)')

    c.setFont('FreeSansIt', 76 * w / 2241)
    if user and user.get_pastor():
        c.drawString(750 * w / 2241, 485 * w / 2241, '{} {}'.format(
            user.get_pastor().last_name, user.get_pastor().first_name) if user and user.get_pastor() else '')
    if user and user.get_bishop():
        c.drawString(750 * w / 2241, 335 * w / 2241, '{} {}'.format(
            user.get_bishop().last_name, user.get_bishop().first_name) if user and user.get_bishop() else '')

    c.setFillColorRGB(1, 1, 1)
    barcode_font_size = 140 * w / 2241
    barcode = createBarcodeDrawing('Code128', value=code, lquiet=0,
                                   barWidth=1.25, barHeight=665 / 2 * w / 2241,
                                   humanReadable=True,
                                   fontSize=barcode_font_size, fontName='FreeSans')
    drawing_width = 1688 / 2 * w / 2241
    barcode_scale = drawing_width / barcode.width
    drawing_height = barcode.height * barcode_scale
    drawing = Drawing(drawing_width, drawing_height)
    drawing.scale(barcode_scale, barcode_scale)
    drawing.add(barcode, name='barcode')
    drawing_rotated = Drawing(drawing_height, drawing_width)
    drawing_rotated.rotate(90)
    drawing_rotated.translate(0, -drawing_height)
    drawing_rotated.add(drawing, name='drawing')
    renderPDF.draw(drawing_rotated, c, 1774 * w / 2241, 380 * w / 2241)
    c.showPage()
