# -*- coding: utf-8 -*-
from flask import request, jsonify, render_template
from datetime import datetime
from forms import PostCodeForm
from config import *
from models import *
from logging.handlers import RotatingFileHandler
import logging


def fullname(user_id):
    name = db.session.query(User.last_name, User.first_name, CustomUser.middle_name).join(CustomUser).filter(
        User.id == user_id).first()
    return '%s %s %s' % (name[0], name[1], name[2])


def create_anket_passes(anket_id):
    create = """INSERT INTO summit_anketpasses
                (anket_id, datetime)
                VALUES
                (%s, CURRENT_TIMESTAMP)
    """ % anket_id
    db.engine.execute(create)


def get_visitor(summit_id, code):
    visitor = db.session.query(SummitAnket).join(Summit).filter(
        Summit.id == summit_id, SummitAnket.code == code).first()

    return visitor


def get_or_create_anket_status(anket_id):
    anket_status = db.session.query(AnketStatus).filter(AnketStatus.anket_id == anket_id).first()
    if not anket_status:
        create = """
                INSERT INTO summit_anketstatus
                (anket_id, reg_code_requested, active)
                VALUES
                (%s, false, true)
                """ % anket_id
        db.engine.execute(create)


def get_anket_data(anket_id):
    get_or_create_anket_status(anket_id)
    query = """SELECT
              anket.id,
              u.image,
              anket.code,
              COUNT (passes.id),
              status.active,
              u.user_ptr_id
              FROM summit_summitanket anket
              JOIN account_customuser u on anket.user_id = u.user_ptr_id
              JOIN summit_anketstatus status on anket.id = status.anket_id
              LEFT OUTER JOIN summit_anketpasses as passes ON (anket.id = passes.anket_id
              AND to_char(passes.datetime, 'YYYY-MM-DD') = '{0}')
              WHERE anket.id = {1}
              GROUP BY anket.id, u.user_ptr_id, u.image, anket.code, status.active;""".format(
        datetime.now().date().strftime('%Y-%m-%d'), anket_id)
    result = db.engine.execute(query)
    data = []
    for row in result:
        data.append(row)
    data = data[0]

    if data[4]:
        create_anket_passes(anket_id)

    anket_data = {'visitor_id': data[0],
                  'profile_image': 'https://vocrm.net/media/' + data[1],
                  'ticket_id': data[2],
                  'passes_count': (data[3] + 1) if data[4] else data[3],
                  'active': data[4],
                  'fullname': fullname(data[5])}

    return anket_data


# Views
@app.route('/', methods=['GET', 'POST'])
def index():
    form = PostCodeForm()

    if request.method == 'POST' and not request.json:
        try:
            code = form.data.get('code')  # 04031153
            summit_id = int(form.data.get('summit'))  # 9
        except Exception as e:
            app.logger.error('Error in POST form: %s\n\n' % e)
            response = jsonify({'message': 'Invalid data type. Available types: JSON, form/data'})
            response.status_code = 400
            return response

        app.logger.error(
            'Received data from Form: '
            'Code: %s. Summit_id: %s' % (code, summit_id))

        if not (code and summit_id):
            app.logger.error(
                'Invalid request. Form data {code} or {summit_id} not passed.\n\n')

        try:
            visitor = get_visitor(summit_id, code)
        except Exception as e:
            app.logger.error('Can"t calculated visitor. Error: %s\n\n' % e)
            visitor = False

        if not visitor:
            app.logger.error('Anket not found - 404.\n')
            return render_template('index.html', form=form, message='БИЛЕТ НЕ НАЙДЕН')

        app.logger.error('Calculated visitor with id = %s' % visitor.id)

        anket_data = get_anket_data(visitor.id)

        app.logger.error('Calculated summit visitors data: %s' % anket_data)

        anket_data['active'] = ('Статус: ' + 'Активен') if anket_data['active'] else ''
        if not anket_data['active']:
            anket_data.pop('active')
            anket_data['message'] = 'ЗАБЛОКИРОВАН!'
        anket_data['passes_count'] = 'Количество проходов: ' + str(anket_data.get('passes_count'))

        app.logger.error('<< Finish >>. Send response.\n\n')

        return render_template('index.html', form=form, **anket_data)

    if request.method == 'POST' and request.json:

        token = request.headers.get('Visitors-Location-Token')
        if not token or token != VISITORS_LOCATION_TOKEN:
            app.logger.error(
                'Request with invalid token - {%s}\n\n' % token)

            response = jsonify({'message': 'Invalid or missing API key'})
            response.status_code = 400
            return response

        try:
            code = request.json.get('code')
            summit_id = request.json.get('summit_id')
        except Exception as e:
            app.logger.error('Invalid request to API. Error:\n\n%s ' % e)
            response = jsonify({'message': 'Invalid data type. Available types: JSON, form/data'})
            response.status_code = 400
            return response

        app.logger.error(
            'Received request to API with data: code - %s, summit_id - %s' % (code, summit_id)
        )

        if code and summit_id:
            visitor = get_visitor(summit_id, code)

            if not visitor:
                response = jsonify({'message': 'Visitor not found'})
                response.status_code = 404
                return response

            app.logger.error('Calculated visitor with id = %s' % visitor.id)

        else:
            app.logger.error('Request to API without {code} or/and {summit_id} params\n\n')

            response = jsonify({'message': 'Params {code} and {summit_id} must be passes'})
            response.status_code = 400
            return response

        try:
            anket_data = get_anket_data(visitor.id)
        except Exception as e:
            app.logger.error('Can"t calculate anket_data. Error: %s\n\n')
            anket_data = False

        if not anket_data:
            app.logger.error('Anket not found - 404.\n\n')

        app.logger.error('Calculated anket_data: %s' % anket_data)

        response = jsonify(anket_data)
        response.status_code = 200

        app.logger.error('<< Finish >>. Send API response.\n\n')

        return response

    return render_template('index.html', form=form)


if __name__ == '__main__':
    handler = RotatingFileHandler('scanner_logs.log', maxBytes=10000 * 100, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.run(host=args.ip, port=args.port, threaded=True)
