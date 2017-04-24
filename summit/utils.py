# -*- coding: utf-8
from __future__ import unicode_literals

import os
from io import BytesIO

from PIL import Image, ImageDraw
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

from summit.models import SummitAnket


def generate_ticket(code):
    anket = get_object_or_404(SummitAnket, code=code)
    user = anket.user

    logo = os.path.join(settings.MEDIA_ROOT, 'background.png')

    buffer = BytesIO()

    w = 90 * mm
    h = 58 * mm
    c = canvas.Canvas(buffer, pagesize=(w, h))
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansBold', 'FreeSansBold.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansIt', 'FreeSansOblique.ttf'))

    pastor = user.get_pastor()
    bishop = user.get_bishop()
    uu = {
        'name': '{} {}'.format(user.last_name, user.first_name),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'image': user.image.path,
        'code': anket.code,
        'pastor': ''.format(pastor.last_name, pastor.first_name) if pastor else '',
        'bishop': ''.format(bishop.last_name, bishop.first_name) if bishop else '',
    }

    create_ticket_page(c, logo, w, h, uu)
    c.save()
    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_ticket_by_summit(anket_ids):
    logo = os.path.join(settings.MEDIA_ROOT, 'background.png')

    buffer = BytesIO()

    w = 90 * mm
    h = 58 * mm
    c = canvas.Canvas(buffer, pagesize=(w, h))
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansBold', 'FreeSansBold.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansIt', 'FreeSansOblique.ttf'))

    raw = """
    SELECT a.id, a.code, u1.image,
      CASE WHEN h.level=4 THEN 'bishop'
           WHEN h.level=2 THEN 'pastor'
           ELSE ''
      END AS hierarchy_level,
      CASE WHEN h.level IN (2, 4) THEN concat(uu2.last_name, ' ', uu2.first_name)
        ELSE '' END
       AS master_name,
      concat(uu1.last_name, ' ', uu1.first_name) AS user_name
    FROM summit_summitanket a
      INNER JOIN account_customuser u1 ON a.user_id = u1.user_ptr_id
      LEFT JOIN account_customuser u2 ON u1.lft > u2.lft AND u1.rght < u2.rght AND u1.tree_id = u2.tree_id
      INNER JOIN auth_user uu1 ON u1.user_ptr_id = uu1.id
      LEFT JOIN auth_user uu2 ON u2.user_ptr_id = uu2.id
      LEFT JOIN hierarchy_hierarchy h ON u2.hierarchy_id = h.id
      WHERE a.id IN ({})
      ORDER BY a.id;
    """.format(','.join([str(a) for a in anket_ids]))
    users = SummitAnket.objects.raw(raw)
    uu = dict()
    for u in users:
        if u.id not in uu.keys():
            name = u.user_name.split(maxsplit=1)
            uu[u.id] = {
                'name': u.user_name,
                'first_name': name[1] if len(name) > 1 else '',
                'last_name': u.user_name.split()[0],
                'image': u.image,
                'code': u.code,
            }
        if u.hierarchy_level == 'pastor':
            uu[u.id]['pastor'] = u.master_name
        elif u.hierarchy_level == 'bishop':
            uu[u.id]['bishop'] = u.master_name
    for u in uu.values():
        create_ticket_page(c, logo, w, h, u)
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


def create_ticket_page(c, logo, w, h, u):
    try:
        c.drawImage(logo, (w - 51 * mm) / 2, (h - 51 * mm) / 2, width=51 * mm, height=51 * mm, mask='auto')
    except OSError:
        pass
    try:
        if u['image']:
            im = Image.open(os.path.join(settings.MEDIA_ROOT, u['image']))
            im = to_circle(im)
            ir = ImageReader(im)
            c.drawImage(ir, 7 * mm, 31 * mm, width=20 * mm, height=20 * mm, mask='auto')
    except ValueError:
        pass
    except OSError:
        pass
    c.setFillColor(HexColor('0x3f4e55'))
    c.setFont('FreeSansBold', 126 * w / 2241)
    c.drawString(750 * w / 2241, 925 * w / 2241, u['last_name'])
    c.drawString(750 * w / 2241, 775 * w / 2241, u['first_name'])
    c.setFillColor(HexColor('0x66787f'))

    c.setFont('FreeSansIt', 51 * w / 2241)
    if u.get('pastor'):
        c.drawString(450 * w / 2241, 485 * w / 2241, '(пастор)')
    if u.get('bishop'):
        c.drawString(450 * w / 2241, 335 * w / 2241, '(епископ)')

    c.setFont('FreeSansIt', 76 * w / 2241)
    if u.get('pastor'):
        c.drawString(750 * w / 2241, 485 * w / 2241, u['pastor'])
    if u.get('bishop'):
        c.drawString(750 * w / 2241, 335 * w / 2241, u['bishop'])

    c.setFillColorRGB(1, 1, 1)
    barcode_font_size = 140 * w / 2241
    barcode = createBarcodeDrawing('Code128', value=u['code'], lquiet=0,
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
