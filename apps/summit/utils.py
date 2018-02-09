# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime
from typing import List, NamedTuple

import os
from PIL import Image, ImageDraw
from django.conf import settings
from django.db import connection
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from io import BytesIO
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak
from rest_framework import exceptions

from apps.summit.models import SummitAnket


class Bishop(NamedTuple):
    pk: int
    user_name: str
    phone_number: str
    attended: List[bool]


class Profile(NamedTuple):
    code: str
    user_name: str
    master_name: str
    phone: str
    ticket_status: str
    attended: str
    level: int
    tree: List[int]
    user_id: int


def get_report_by_bishop_or_high(
        summit_id: int,
        report_date: datetime,
        department: int = None,
        fio: str = '',
        hierarchy: int = None):
    fio_filter = ['']
    name_params = list()
    for name in filter(lambda name: bool(name), fio.replace(',', ' ').split(' ')):
        fio_filter.append(
            "(bbu.last_name ilike %s or "
            "bbu.first_name ilike %s or "
            "bu.middle_name ilike %s)")
        name_params += ['%'+name+'%'] * 3
    query = """
        SELECT DISTINCT ON (bu.user_ptr_id) bu.user_ptr_id pk,
            concat(bbu.last_name, ' ', bbu.first_name, ' ', bu.middle_name) user_name,
            bu.phone_number phone_number,
            array(
                WITH RECURSIVE t AS (
                  SELECT user_id,
                    exists(
                   SELECT at.id
                   FROM summit_summitattend at
                   WHERE at.anket_id = summit_summitanket.id AND at.date = '{date}') attended
                  FROM summit_summitanket
                    JOIN account_customuser a ON user_id = a.user_ptr_id
                    JOIN auth_user u ON a.user_ptr_id = u.id
                  WHERE summit_summitanket.user_id = ba.user_id and summit_id = %s
                  UNION
                  SELECT summit_summitanket.user_id ,exists(
                   SELECT at.id
                   FROM summit_summitattend at
                   WHERE at.anket_id = summit_summitanket.id AND at.date = '{date}') attended
                  FROM summit_summitanket
                    JOIN t ON summit_summitanket.author_id = t.user_id
                    JOIN account_customuser customuser ON summit_summitanket.user_id = customuser.user_ptr_id
                    JOIN auth_user u2 ON customuser.user_ptr_id = u2.id
                  WHERE summit_summitanket.summit_id = %s
                )
                SELECT attended
                FROM t
            ) attended
        FROM summit_summitanket ba
          INNER JOIN account_customuser bu ON ba.user_id = bu.user_ptr_id
          JOIN auth_user bbu ON bbu.id = bu.user_ptr_id
          JOIN hierarchy_hierarchy h ON bu.hierarchy_id = h.id
          JOIN account_customuser_departments bud ON bud.customuser_id = bu.user_ptr_id
        WHERE summit_id = %s and h.level > 3 {department}{search_fio}{hierarchy};
        """.format(
        date=report_date.strftime('%Y-%m-%d'),
        department=' and bud.department_id = %s' if department else '',
        search_fio=' and '.join(fio_filter),
        hierarchy=' and h.id = %s' if hierarchy else ''
    )
    params = [summit_id, summit_id, summit_id]
    if department:
        params.append(department)
    params += name_params
    if hierarchy:
        params.append(hierarchy)
    bishops: List[Bishop] = list()
    with connection.cursor() as connect:
        connect.execute(query, params)
        for bishop in connect.fetchall():
            bishops.append(Bishop(*bishop))

    return sorted([{
        'id': b.pk,
        'user_name': b.user_name,
        'total': len(b.attended),
        'absent': len([a for a in b.attended if not a]),
        'attend': len([a for a in b.attended if a]),
        'phone_number': b.phone_number
    } for b in bishops], key=lambda b: b['user_name'])


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(181 * mm, 7 * mm,
                             "Page %d of %d" % (self._pageNumber, page_count))


class SummitParticipantReport(object):
    def __init__(self, summit_id, master, report_date, short=None, attended=None):
        self.summit_id = summit_id
        self.short = short
        self.attended = attended
        self.master = master
        if report_date:
            try:
                self.report_date = datetime.strptime(report_date, '%Y-%m-%d')
            except ValueError:
                raise exceptions.ValidationError({'detail': _('Invalid date.')})
        else:
            self.report_date = datetime.now()
        self.elements = list()
        self.names = dict()
        self._init_styles()
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer, rightMargin=72, leftMargin=72, topMargin=22, bottomMargin=22, pagesize=A4)
        self.width = self.doc.width

    def _init_styles(self):
        pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
        pdfmetrics.registerFont(TTFont('FreeSansBold', 'FreeSansBold.ttf'))
        pdfmetrics.registerFont(TTFont('FreeSansIt', 'FreeSansOblique.ttf'))

        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='RightAlign', fontName='FreeSans', alignment=TA_RIGHT, fontSize=8))
        self.styles.add(ParagraphStyle(name='LeftAlign', fontName='FreeSans', alignment=TA_LEFT, fontSize=8))
        self.styles.add(ParagraphStyle(name='date', fontName='FreeSans', alignment=TA_RIGHT, fontSize=12))
        self.styles.add(ParagraphStyle(
            name='Header1', fontName='FreeSansBold', alignment=TA_LEFT, fontSize=16, spaceAfter=5))
        self.styles.add(ParagraphStyle(
            name='Header12', fontName='FreeSansBold', alignment=TA_LEFT, fontSize=14, spaceAfter=5))
        self.styles.add(ParagraphStyle(
            name='Header2', fontName='FreeSans', alignment=TA_LEFT, fontSize=12, spaceAfter=5))

    def _append_document_header(self):
        self.elements.append(Paragraph(
            'Отчет создан: {}'.upper().format(datetime.now().strftime('%d.%m.%Y %H:%M:%S')), self.styles['date']))
        self.elements.append(Paragraph(
            'Отчет о посещаемости за {}'.upper().format(self.report_date.strftime('%d.%m.%Y')), self.styles['Header1']))
        self.elements.append(Paragraph(self.master.fullname.upper(), self.styles['Header12']))

    def _append_table_header(self, user):
        self.names[user.user_level] = user.user_name
        levels = sorted(list(self.names.keys()))
        self.elements.append(Paragraph(
            ' > '.join([self.names[k] for k in levels if k <= user.user_level]), self.styles['Header2']))

    def _append_tables(self, users):
        if self.attended and self.attended.upper() in ('TRUE', 'T', 'YES', 'Y', '1'):
            table_users = list(filter(lambda u: u.attended, users))
        elif self.attended and self.attended.upper() in ('FALSE', 'F', 'NO', 'N', '0'):
            table_users = list(filter(lambda u: not u.attended, users))
        else:
            table_users = users
        for user in users:
            self._append_user_table(user, table_users)

    def _append_user_table(self, u, users):
        table_data = []
        red_lines = []
        for user in users:
            if u.user_id == user.master_id:
                table_data.append(
                    [user.attended if user.attended else '   ', user.user_name, user.get_ticket_status_display(),
                     user.phone, user.code,
                     True if user.ticket_status == SummitAnket.PRINTED else False])
        table_data = sorted(table_data, key=lambda a: a[1])
        for l, t in enumerate(table_data):
            if t[5]:
                red_lines.append(l + 1)
            table_data[l] = table_data[l][:-1]
        if not table_data:
            return
        self._append_table_header(u)

        table_data = [['Был', 'ФИО', 'Билет', 'Номер телефона', 'Код']] + table_data
        user_table = Table(table_data, colWidths=[
            self.width * 0.1, self.width * 0.5, self.width * 0.2, self.width * 0.2], normalizedData=1)

        red_cells = [('TEXTCOLOR', (2, line), (2, line), colors.red) for line in red_lines]
        red_cells += [('FONT', (2, line), (2, line), 'FreeSansBold') for line in red_lines]
        user_table.setStyle(TableStyle([
                                           ('INNERGRID', (0, 0), (-1, -1), 0.15, colors.black),
                                           ('FONT', (0, 0), (-1, -1), 'FreeSans'),
                                           ('FONTSIZE', (0, 0), (-1, -1), 8),
                                           ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                                           ('BOX', (0, 0), (-1, -1), 0.15, colors.black),

                                           # ('FONTSIZE', (0, 0), (0, -1), 10),
                                           ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                           ('TOPPADDING', (0, 0), (-1, -1), 1),

                                           ('FONTSIZE', (0, 0), (-1, 0), 8),
                                           ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                           ('FONT', (0, 0), (-1, 0), 'FreeSansBold'),
                                           ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                       ] + red_cells))
        self.elements.append(user_table)
        if self.short is None:
            self.elements.append(PageBreak())

    def _get_participants(self):
        raw = """
            SELECT a.id, a.code, u.phone_number phone, a.user_id, u.master_id, u.depth user_level,
              h.level hierarchy_level, a.ticket_status ticket_status,
              concat(uu.last_name, ' ', uu.first_name, ' ', u.middle_name) user_name,
              (select COALESCE(to_char(at.time, 'HH24:MI:SS'), to_char(at.created_at, 'HH24:MI:SS el'), '+')
              from summit_summitattend at WHERE at.anket_id = a.id AND at.date = '{date}' LIMIT 1) as attended
            FROM summit_summitanket a
              INNER JOIN account_customuser u ON a.user_id = u.user_ptr_id
              INNER JOIN auth_user uu ON u.user_ptr_id = uu.id
              LEFT JOIN hierarchy_hierarchy h ON u.hierarchy_id = h.id
              WHERE (u.path like '{path}%%' AND u.depth >= {depth} AND summit_id = {summit_id})
              ORDER BY u.path;
        """.format(
            date=self.report_date.strftime('%Y-%m-%d'),
            path=self.master.path,
            depth=self.master.depth,
            summit_id=self.summit_id
        )
        return list(SummitAnket.objects.raw(raw))

    def build(self):
        self.doc.build(self.elements, canvasmaker=NumberedCanvas)
        pdf = self.buffer.getvalue()
        self.buffer.close()

        return pdf

    def generate_pdf(self):
        users = self._get_participants()
        self._append_document_header()
        total = len(users)
        absent = len(tuple(filter(lambda u: not u.attended, users)))
        self.elements.append(Paragraph('Всего: {total} / Отсутствует: {absent}'.format(total=total, absent=absent),
                                       self.styles['Header12']))
        self._append_tables(users)

        return self.build()


class FullSummitParticipantReport(object):
    def __init__(self, summit_id, master, report_date, short=None, attended=None):
        self.summit_id = summit_id
        self.short = short
        self.attended = attended
        self.master = master
        if report_date:
            try:
                self.report_date = datetime.strptime(report_date, '%Y-%m-%d')
            except ValueError:
                raise exceptions.ValidationError({'detail': _('Invalid date.')})
        else:
            self.report_date = datetime.now()
        self.elements = list()
        self._init_styles()
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer, rightMargin=72, leftMargin=72, topMargin=22, bottomMargin=22, pagesize=A4)
        self.width = self.doc.width

    def _init_styles(self):
        pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
        pdfmetrics.registerFont(TTFont('FreeSansBold', 'FreeSansBold.ttf'))
        pdfmetrics.registerFont(TTFont('FreeSansIt', 'FreeSansOblique.ttf'))

        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='RightAlign', fontName='FreeSans', alignment=TA_RIGHT, fontSize=8))
        self.styles.add(ParagraphStyle(name='LeftAlign', fontName='FreeSans', alignment=TA_LEFT, fontSize=8))
        self.styles.add(ParagraphStyle(name='date', fontName='FreeSans', alignment=TA_RIGHT, fontSize=12))
        self.styles.add(ParagraphStyle(
            name='Header1', fontName='FreeSansBold', alignment=TA_LEFT, fontSize=16, spaceAfter=5))
        self.styles.add(ParagraphStyle(
            name='Header12', fontName='FreeSansBold', alignment=TA_LEFT, fontSize=14, spaceAfter=5))
        self.styles.add(ParagraphStyle(
            name='Header2', fontName='FreeSans', alignment=TA_LEFT, fontSize=12, spaceAfter=5))

    def _append_document_header(self):
        self.elements.append(Paragraph(
            'Отчет создан: {}'.upper().format(datetime.now().strftime('%d.%m.%Y %H:%M:%S')), self.styles['date']))
        self.elements.append(Paragraph(
            'Отчет о посещаемости за {}'.upper().format(self.report_date.strftime('%d.%m.%Y')), self.styles['Header1']))
        self.elements.append(Paragraph(self.master.fullname.upper(), self.styles['Header12']))

    def _append_table_header(self, user: Profile):
        self.elements.append(Paragraph(user.user_name, self.styles['Header2']))

    def _append_tables(self, users: List[Profile]):
        if self.attended and self.attended.upper() in ('TRUE', 'T', 'YES', 'Y', '1'):
            table_users = list(filter(lambda u: u.attended, users))
        elif self.attended and self.attended.upper() in ('FALSE', 'F', 'NO', 'N', '0'):
            table_users = list(filter(lambda u: not u.attended, users))
        else:
            table_users = users
        user = users[0]
        self._append_user_table(user, table_users)

    def _append_user_table(self, u: Profile, users: List[Profile]):
        table_data = []
        for user in users:
            table_data.append(
                [user.attended if user.attended else '   ', user.user_name, user.master_name,
                 user.phone, user.code,
                 True if user.ticket_status == SummitAnket.PRINTED else False])
        table_data = sorted(table_data, key=lambda a: a[1])
        for l, t in enumerate(table_data):
            table_data[l] = table_data[l][:-1]
        if not table_data:
            return
        self._append_table_header(u)

        table_data = [['Был', 'ФИО', 'Ответственный', 'Номер телефона', 'Код']] + table_data
        user_table = Table(table_data, colWidths=[
            self.width * 0.1, self.width * 0.35, self.width * 0.35, self.width * 0.2], normalizedData=1)

        user_table.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.15, colors.black),
            ('FONT', (0, 0), (-1, -1), 'FreeSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 0.15, colors.black),

            # ('FONTSIZE', (0, 0), (0, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 1),

            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 0), (-1, 0), 'FreeSansBold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]))
        self.elements.append(user_table)
        if self.short is None:
            self.elements.append(PageBreak())

    def _get_participants(self) -> List[Profile]:
        """

        :return: list of Profile[code, user_name, master_name, phone, ticket_status, attended]
        """
        raw = """
        WITH RECURSIVE t AS (
          SELECT summit_summitanket.code,
            concat(u.last_name, ' ', u.first_name, ' ', a.middle_name) user_name,
            concat(mu.last_name, ' ', mu.first_name, ' ', mcu.middle_name) master_name,
            a.phone_number phone,
            ticket_status,
            1 as level, array[user_id] as tree,
              (select COALESCE(to_char(at.time, 'HH24:MI:SS'), to_char(at.created_at, 'HH24:MI:SS el'), '+')
               from summit_summitattend at
               WHERE at.anket_id = summit_summitanket.id AND at.date = '{date}' LIMIT 1) as attended,
            user_id
          FROM summit_summitanket
            JOIN account_customuser a ON user_id = a.user_ptr_id
            JOIN auth_user u ON a.user_ptr_id = u.id
            LEFT OUTER JOIN account_customuser mcu ON a.master_id = mcu.user_ptr_id
            LEFT OUTER JOIN auth_user mu ON mcu.user_ptr_id = mu.id
          WHERE summit_summitanket.user_id = {master_id} and summit_id = %s
          UNION
          SELECT summit_summitanket.code,
            concat(u2.last_name, ' ', u2.first_name, ' ', customuser.middle_name) user_name,
            concat(mu2.last_name, ' ', mu2.first_name, ' ', mcu2.middle_name) master_name,
            customuser.phone_number phone,
            summit_summitanket.ticket_status,
            t.level + 1 as level, array_cat(t.tree, array[summit_summitanket.user_id]) as tree,
              (select COALESCE(to_char(at.time, 'HH24:MI:SS'), to_char(at.created_at, 'HH24:MI:SS el'), '+')
               from summit_summitattend at
               WHERE at.anket_id = summit_summitanket.id AND at.date = '{date}' LIMIT 1) as attended,
            summit_summitanket.user_id
          FROM summit_summitanket
            JOIN t ON summit_summitanket.author_id = t.user_id
            JOIN account_customuser customuser ON summit_summitanket.user_id = customuser.user_ptr_id
            JOIN auth_user u2 ON customuser.user_ptr_id = u2.id
            LEFT OUTER JOIN account_customuser mcu2 ON customuser.master_id = mcu2.user_ptr_id
            LEFT JOIN auth_user mu2 ON mcu2.user_ptr_id = mu2.id
          WHERE summit_summitanket.summit_id = %s
        )
        SELECT code, user_name, master_name, phone, ticket_status, attended, level, tree, user_id
        FROM t ORDER BY tree;
        """.format(
            date=self.report_date.strftime('%Y-%m-%d'),
            master_id=self.master.id,
        )
        profiles: List[Profile] = list()
        with connection.cursor() as connect:
            connect.execute(raw, [self.summit_id, self.summit_id])
            for profile in connect.fetchall():
                profiles.append(Profile(*profile))

        return profiles

    def build(self):
        self.doc.build(self.elements, canvasmaker=NumberedCanvas)
        pdf = self.buffer.getvalue()
        self.buffer.close()

        return pdf

    def generate_pdf(self):
        users = self._get_participants()
        self._append_document_header()
        total = len(users)
        absent = len(tuple(filter(lambda u: not u.attended, users)))
        self.elements.append(Paragraph('Всего: {total} / Отсутствует: {absent}'.format(total=total, absent=absent),
                                       self.styles['Header12']))
        self._append_tables(users)

        return self.build()


def generate_ticket(code):
    anket = get_object_or_404(SummitAnket, code=code)
    user = anket.user

    logo = os.path.join(settings.MEDIA_ROOT, 'background.png')

    buffer = BytesIO()

    w = .035 * A4[0] * cm
    h = w * 941 / 2241
    c = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansBold', 'FreeSansBold.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSansIt', 'FreeSansOblique.ttf'))

    pastor = user.get_pastor()
    bishop = user.get_bishop()
    uu = {
        'name': '{} {}'.format(user.last_name, user.first_name),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'image': user.image.path if user.image else None,
        'code': anket.code,
        'pastor': '{} {}'.format(pastor.last_name, pastor.first_name) if pastor else '',
        'bishop': '{} {}'.format(bishop.last_name, bishop.first_name) if bishop else '',
    }

    create_ticket_page(c, logo, w, h, uu)
    c.save()
    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_ticket_by_summit(ankets):
    logo = os.path.join(settings.MEDIA_ROOT, 'background.png')

    buffer = BytesIO()

    w = .035 * A4[0] * cm
    h = w * 941 / 2241
    c = canvas.Canvas(buffer, pagesize=A4)
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
      LEFT JOIN account_customuser u2 ON u1.path like u2.path||'%%' AND u1.depth >= u2.depth
      INNER JOIN auth_user uu1 ON u1.user_ptr_id = uu1.id
      LEFT JOIN auth_user uu2 ON u2.user_ptr_id = uu2.id
      LEFT JOIN hierarchy_hierarchy h ON u2.hierarchy_id = h.id
      WHERE a.id IN ({})
      ORDER BY a.id;
    """.format(','.join([str(a[0]) for a in ankets]))
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
    v = .035 * A4[1] * cm - h
    try:
        c.drawImage(logo, 0, v, width=w, height=h, mask='auto')
    except OSError:
        pass
    # try:
    #     if u['image']:
    #         im = Image.open(os.path.join(settings.MEDIA_ROOT, u['image']))
    #         im = to_circle(im)
    #         ir = ImageReader(im)
    #         c.drawImage(ir, 7 * mm, 31 * mm, width=20 * mm, height=20 * mm, mask='auto')
    # except ValueError:
    #     pass
    # except OSError:
    #     pass
    c.setFillColor(HexColor('0x3f4e55'))
    c.setFont('FreeSansBold', 46 * w / 2241)
    c.drawString(80 * w / 2241, 165 * w / 2241 + v, u['last_name'])
    c.drawString(970 * w / 2241, 165 * w / 2241 + v, u['first_name'])
    # c.setFillColor(HexColor('0x66787f'))

    # c.setFont('FreeSansIt', 51 * w / 2241)
    # if u.get('pastor'):
    #     c.drawString(450 * w / 2241, 485 * w / 2241, '(пастор)')
    # if u.get('bishop'):
    #     c.drawString(450 * w / 2241, 335 * w / 2241, '(епископ)')
    #
    # c.setFont('FreeSansIt', 76 * w / 2241)
    # if u.get('pastor'):
    #     c.drawString(750 * w / 2241, 485 * w / 2241, u['pastor'])
    # if u.get('bishop'):
    #     c.drawString(750 * w / 2241, 335 * w / 2241, u['bishop'])

    c.setFillColorRGB(1, 1, 1)
    barcode_font_size = 70 * w / 2241
    barcode = createBarcodeDrawing('Code128', value=u['code'], lquiet=0,
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
