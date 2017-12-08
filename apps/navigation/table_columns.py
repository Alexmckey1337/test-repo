from collections import OrderedDict
from copy import deepcopy

from apps.account.models import CustomUser

church_columns = {
    'get_title': {
        'id': 0, 'title': 'Название церкви', 'ordering_title': 'title', 'number': 1, 'active': True, 'editable': False},
    'department': {
        'id': 0, 'title': 'Отдел', 'ordering_title': 'department__title', 'number': 2, 'active': True, 'editable': True},
    'city': {
        'id': 0, 'title': 'Город', 'ordering_title': 'city', 'number': 3, 'active': True, 'editable': True},
    'pastor': {
        'id': 0, 'title': 'Пастор Церкви', 'ordering_title': 'pastor__last_name', 'number': 4, 'active': True, 'editable': True},
    'is_open': {
        'id': 0, 'title': 'Открыта', 'ordering_title': 'is_open', 'number': 5, 'active': True, 'editable': True},
    'address': {
        'id': 0, 'title': 'Адрес', 'ordering_title': 'address', 'number': 6, 'active': True, 'editable': True},
    'phone_number': {
        'id': 0, 'title': 'Телефонный номер', 'ordering_title': 'phone_number', 'number': 7, 'active': True, 'editable': True},
    'website': {
        'id': 0, 'title': 'Адрес сайта', 'ordering_title': 'website', 'number': 8, 'active': True, 'editable': True},
    'country': {
        'id': 0, 'title': 'Страна', 'ordering_title': 'country', 'number': 9, 'active': True, 'editable': True},
    'opening_date': {
        'id': 0, 'title': 'Дата открытия', 'ordering_title': 'opening_date', 'number': 10, 'active': True, 'editable': True}
}

user_columns = {
    'fullname': {
        'id': 0, 'title': 'ФИО', 'ordering_title': 'last_name', 'number': 1, 'active': True, 'editable': False},
    'email': {
        'id': 0, 'title': 'Email', 'ordering_title': 'email', 'number': 2, 'active': True, 'editable': True},
    'phone_number': {
        'id': 0, 'title': 'Номер телефона', 'ordering_title': 'phone_number', 'number': 3, 'active': True, 'editable': True},
    'born_date': {
        'id': 0, 'title': 'Дата рождения', 'ordering_title': 'born_date', 'number': 4, 'active': True, 'editable': True},
    'hierarchy': {
        'id': 0, 'title': 'Иерархия', 'ordering_title': 'hierarchy__level', 'number': 5, 'active': True, 'editable': True},
    'departments': {
        'id': 0, 'title': 'Отдел', 'ordering_title': 'department_title', 'number': 6, 'active': True, 'editable': True},
    'country': {
        'id': 0, 'title': 'Страна', 'ordering_title': 'country', 'number': 7, 'active': True, 'editable': True},
    'region': {
        'id': 0, 'title': 'Область', 'ordering_title': 'region', 'number': 8, 'active': True, 'editable': True},
    'city': {
        'id': 0, 'title': 'Населенный пункт', 'ordering_title': 'city', 'number': 9, 'active': True, 'editable': True},
    'district': {
        'id': 0, 'title': 'Район', 'ordering_title': 'district', 'number': 10, 'active': True, 'editable': True},
    'address': {
        'id': 0, 'title': 'Адрес', 'ordering_title': 'address', 'number': 11, 'active': True, 'editable': True},
    'social': {
        'id': 0, 'title': 'Социальные сети', 'ordering_title': 'facebook', 'number': 12, 'active': True, 'editable': True},
    'divisions': {
        'id': 0, 'title': 'Служения', 'ordering_title': 'divisions', 'number': 13, 'active': True, 'editable': True},
    'master': {
        'id': 0, 'title': 'Ответственный', 'ordering_title': 'master__last_name', 'number': 14, 'active': True, 'editable': True},
    'repentance_date': {
        'id': 0, 'title': 'Дата покаяния', 'ordering_title': 'repentance_date', 'number': 15, 'active': True, 'editable': True},
    'spiritual_level': {
        'id': 0, 'title': 'Духовный уровень', 'ordering_title': 'spiritual_level', 'number': 16, 'active': True, 'editable': True},
    'get_church': {
        'id': 0, 'title': 'Церковь', 'ordering_title': '', 'number': 17, 'active': True, 'editable': True},
}

partner_columns = {
    'user.fullname': {
        'id': 0, 'title': 'ФИО', 'ordering_title': 'user__last_name', 'number': 1, 'active': True, 'editable': False},
    'user.email': {
        'id': 0, 'title': 'Email', 'ordering_title': 'user__email', 'number': 2, 'active': True, 'editable': True},
    'user.phone_number': {
        'id': 0, 'title': 'Номер телефона', 'ordering_title': 'user__phone_number', 'number': 3, 'active': True, 'editable': True},
    'user.born_date': {
        'id': 0, 'title': 'Дата рождения', 'ordering_title': 'user__born_date', 'number': 4, 'active': True, 'editable': True},
    'user.hierarchy.title': {
        'id': 0, 'title': 'Иерархия', 'ordering_title': 'user__hierarchy__level', 'number': 5, 'active': True, 'editable': True},
    'user.departments': {
        'id': 0, 'title': 'Отдел', 'ordering_title': 'user__department_title', 'number': 6, 'active': True, 'editable': True},
    'user.country': {
        'id': 0, 'title': 'Страна', 'ordering_title': 'user__country', 'number': 7, 'active': True, 'editable': True},
    'user.region': {
        'id': 0, 'title': 'Область', 'ordering_title': 'user__region', 'number': 8, 'active': True, 'editable': True},
    'user.city': {
        'id': 0, 'title': 'Населенный пункт', 'ordering_title': 'user__city', 'number': 9, 'active': True, 'editable': True},
    'user.district': {
        'id': 0, 'title': 'Район', 'ordering_title': 'user__district', 'number': 10, 'active': True, 'editable': True},
    'user.address': {
        'id': 0, 'title': 'Адрес', 'ordering_title': 'user__address', 'number': 11, 'active': True, 'editable': True},
    'user.social': {
        'id': 0, 'title': 'Социальные сети', 'ordering_title': 'user__facebook', 'number': 12, 'active': True, 'editable': True},
    'user.divisions': {
        'id': 0, 'title': 'Служения', 'ordering_title': 'user__divisions', 'number': 13, 'active': True, 'editable': True},
    'user.master.fullname': {
        'id': 0, 'title': 'Ответственный', 'ordering_title': 'user__master__last_name', 'number': 14, 'active': True, 'editable': True},
    'user.repentance_date': {
        'id': 0, 'title': 'Дата покаяния', 'ordering_title': 'user__repentance_date', 'number': 15, 'active': True, 'editable': True},
    'user.spiritual_level': {
        'id': 0, 'title': 'Духовный уровень', 'ordering_title': 'user__spiritual_level', 'number': 16, 'active': True, 'editable': True},
    'user.get_church': {
        'id': 0, 'title': 'Церковь', 'ordering_title': '', 'number': 17, 'active': True, 'editable': True},
    'group': {
        'id': 0, 'title': 'Тег', 'ordering_title': 'group__title', 'number': 18, 'active': True, 'editable': False},
    'responsible': {
        'id': 0, 'title': 'Менеджер', 'ordering_title': 'responsible__last_name', 'number': 19, 'active': True, 'editable': True},
    'value': {
        'id': 0, 'title': 'Сумма', 'ordering_title': 'value', 'number': 20, 'active': True, 'editable': True},
}

church_partner_columns = {
    'church.get_title': {
        'id': 0, 'title': 'Название церкви', 'ordering_title': 'church__title', 'number': 1, 'active': True, 'editable': False},
    'church.department.title': {
        'id': 0, 'title': 'Отдел', 'ordering_title': 'church__department__title', 'number': 2, 'active': True, 'editable': True},
    'church.city': {
        'id': 0, 'title': 'Город', 'ordering_title': 'church__city', 'number': 3, 'active': True, 'editable': True},
    'church.pastor.fullname': {
        'id': 0, 'title': 'Пастор Церкви', 'ordering_title': 'church__pastor__last_name', 'number': 4, 'active': True, 'editable': True},
    'church.is_open': {
        'id': 0, 'title': 'Открыта', 'ordering_title': 'church__is_open', 'number': 5, 'active': True, 'editable': True},
    'church.address': {
        'id': 0, 'title': 'Адрес', 'ordering_title': 'church__address', 'number': 6, 'active': True, 'editable': True},
    'church.phone_number': {
        'id': 0, 'title': 'Телефонный номер', 'ordering_title': 'church__phone_number', 'number': 7, 'active': True, 'editable': True},
    'church.website': {
        'id': 0, 'title': 'Адрес сайта', 'ordering_title': 'church__website', 'number': 8, 'active': True, 'editable': True},
    'church.country': {
        'id': 0, 'title': 'Страна', 'ordering_title': 'church__country', 'number': 9, 'active': True, 'editable': True},
    'church.opening_date': {
        'id': 0, 'title': 'Дата открытия', 'ordering_title': 'church__opening_date', 'number': 10, 'active': True, 'editable': True},
    'group': {
        'id': 0, 'title': 'Тег', 'ordering_title': 'group__title', 'number': 11, 'active': True, 'editable': False},
    'responsible': {
        'id': 0, 'title': 'Менеджер', 'ordering_title': 'responsible__last_name', 'number': 12, 'active': True, 'editable': True},
    'value': {
        'id': 0, 'title': 'Сумма', 'ordering_title': 'value', 'number': 13, 'active': True, 'editable': True},
}

home_group_columns = {
    'get_title': {
        'id': 0, 'title': 'Название Группы', 'ordering_title': 'title', 'number': 1, 'active': True, 'editable': False},
    'church': {
        'id': 0, 'title': 'Церковь', 'ordering_title': 'church__title', 'number': 2, 'active': True, 'editable': True},
    'city': {
        'id': 0, 'title': 'Город', 'ordering_title': 'city', 'number': 3, 'active': True, 'editable': True},
    'leader': {
        'id': 0, 'title': 'Лидер', 'ordering_title': 'leader__last_name', 'number': 4, 'active': True, 'editable': True},
    'opening_date': {
        'id': 0, 'title': 'Дата открытия', 'ordering_title': 'opening_date', 'number': 5, 'active': True, 'editable': True},
    'address': {
        'id': 0, 'title': 'Адрес', 'ordering_title': 'address', 'number': 6, 'active': True, 'editable': True},
    'phone_number': {
        'id': 0, 'title': 'Телефонный номер', 'ordering_title': 'phone_number', 'number': 7, 'active': True, 'editable': True},
    'website': {
        'id': 0, 'title': 'Адрес сайта', 'ordering_title': 'website', 'number': 8, 'active': True, 'editable': True},
    'count_users': {
        'id': 0, 'title': 'Количество людей', 'ordering_title': 'count_users', 'number': 9, 'active': True, 'editable': True},
}

summit_columns = {
    'full_name': {
        'id': 0, 'title': 'ФИО', 'ordering_title': 'last_name', 'number': 1, 'active': True, 'editable': True},
    'responsible': {
        'id': 0, 'title': 'Ответственный', 'ordering_title': 'responsible', 'number': 2, 'active': True, 'editable': True},
    'spiritual_level': {
        'id': 0, 'title': 'Духовный уровень', 'ordering_title': 'spiritual_level', 'number': 3, 'active': True, 'editable': True},
    'divisions_title': {
        'id': 0, 'title': 'Служения', 'ordering_title': 'divisions_title', 'number': 4, 'active': True, 'editable': True},
    'department': {
        'id': 0, 'title': 'Отдел', 'ordering_title': 'department', 'number': 5, 'active': True, 'editable': True},
    'hierarchy_title': {
        'id': 0, 'title': 'Иерархия', 'ordering_title': 'hierarchy_level', 'number': 6, 'active': True, 'editable': True},
    'phone_number': {
        'id': 0, 'title': 'Номер телефона', 'ordering_title': 'user__phone_number', 'number': 7, 'active': True, 'editable': True},
    'email': {
        'id': 0, 'title': 'Email', 'ordering_title': 'user__email', 'number': 8, 'active': True, 'editable': True},
    'social': {
        'id': 0, 'title': 'Социальные сети', 'ordering_title': 'user__facebook', 'number': 9, 'active': True, 'editable': True},
    'country': {
        'id': 0, 'title': 'Страна', 'ordering_title': 'country', 'number': 10, 'active': True, 'editable': True},
    'city': {
        'id': 0, 'title': 'Населенный пункт', 'ordering_title': 'city', 'number': 11, 'active': True, 'editable': True},
    'region': {
        'id': 0, 'title': 'Область', 'ordering_title': 'user__region', 'number': 12, 'active': True, 'editable': True},
    'district': {
        'id': 0, 'title': 'Район', 'ordering_title': 'user__district', 'number': 13, 'active': True, 'editable': True},
    'address': {
        'id': 0, 'title': 'Адрес', 'ordering_title': 'user__address', 'number': 14, 'active': True, 'editable': True},
    'born_date': {
        'id': 0, 'title': 'Дата рождения', 'ordering_title': 'user__born_date', 'number': 15, 'active': True, 'editable': True},
    'repentance_date': {
        'id': 0, 'title': 'Дата Покаяния', 'ordering_title': 'user__repentance_date', 'number': 16, 'active': True, 'editable': True},
    'code': {
        'id': 0, 'title': 'Код', 'ordering_title': 'code', 'number': 17, 'active': True, 'editable': True},
    'value': {
        'id': 0, 'title': 'Оплата', 'ordering_title': 'value', 'number': 18, 'active': True, 'editable': True},
    'description': {
        'id': 0, 'title': 'Примечания', 'ordering_title': 'description', 'number': 19, 'active': True, 'editable': True},
    'ticket_status': {
        'id': 0, 'title': 'Статус билета', 'ordering_title': 'ticket_status', 'number': 20, 'active': True, 'editable': True},
    'e_ticket': {
        'id': 0, 'title': 'Электронный билет', 'ordering_title': 'status__reg_code_requested', 'number': 21, 'active': True, 'editable': True},
    'has_email': {
        'id': 0, 'title': 'Email отправлен', 'ordering_title': 'has_email', 'number': 22, 'active': True, 'editable': True},
}

meeting_columns = {
    'id': {
        'id': 0, 'title': '№', 'ordering_title': 'id', 'number': 1, 'active': True, 'editable': False},
    'home_group': {
        'id': 0, 'title': 'Домашняя группа', 'ordering_title': 'home_group__title', 'number': 2, 'active': True, 'editable': True},
    'owner': {
        'id': 0, 'title': 'Лидер домашней группы', 'ordering_title': 'owner__last_name', 'number': 3, 'active': True, 'editable': True},
    'phone_number': {
        'id': 0, 'title': 'Телефонный номер', 'ordering_title': 'home_group__phone_number', 'number': 4, 'active': True, 'editable': True},
    'type': {
        'id': 0, 'title': 'Тип отчета', 'ordering_title': 'type__code', 'number': 5, 'active': True, 'editable': True},
    'visitors_attended': {
        'id': 0, 'title': 'Присутствовали', 'ordering_title': 'visitors_attended', 'number': 6, 'active': True, 'editable': True},
    'visitors_absent': {
        'id': 0, 'title': 'Отсутствовали', 'ordering_title': 'visitors_absent', 'number': 7, 'active': True, 'editable': True},
    'total_sum': {
        'id': 0, 'title': 'Сумма пожертвований', 'ordering_title': 'total_sum', 'number': 8, 'active': True, 'editable': True},
    'date': {
        'id': 0, 'title': 'Дата создания', 'ordering_title': 'date', 'number': 9, 'active': True, 'editable': True},
}

attend_columns = {
    'attended': {
        'id': 0, 'title': 'Присутствие', 'ordering_title': 'attended', 'number': 1, 'active': True, 'editable': True},
    'user': {
        'id': 0, 'title': 'ФИО', 'ordering_title': 'user__last_name', 'number': 2, 'active': True, 'editable': False},
    'spiritual_level': {
        'id': 0, 'title': 'Духовный уровень', 'ordering_title': 'user__spiritual_level', 'number': 3, 'active': True, 'editable': True},
    'phone_number': {
        'id': 0, 'title': 'Телефонный номер', 'ordering_title': 'user__phone_number', 'number': 4, 'active': True, 'editable': True},
    'note': {
        'id': 0, 'title': 'Коментарий', 'ordering_title': 'note', 'number': 5, 'active': True, 'editable': True},
}

church_report_columns = {
    'id': {
        'id': 0, 'title': '№', 'ordering_title': 'id', 'number': 1, 'active': True, 'editable': False},
    'date': {
        'id': 0, 'title': 'Дата создания', 'ordering_title': 'date', 'number': 2, 'active': True, 'editable': True},
    'church': {
        'id': 0, 'title': 'Церковь', 'ordering_title': 'church__title', 'number': 3, 'active': True, 'editable': True},
    'pastor': {
        'id': 0, 'title': 'Пастор Церкви', 'ordering_title': 'pastor__last_name', 'number': 4, 'active': True, 'editable': True},
    'total_peoples': {
        'id': 0, 'title': 'Людей на собрании', 'ordering_title': 'count_people', 'number': 5, 'active': True, 'editable': True},
    'total_new_peoples': {
        'id': 0, 'title': 'Новых людей', 'ordering_title': 'new_people', 'number': 6, 'active': True, 'editable': True},
    'total_repentance': {
        'id': 0, 'title': 'Покаяний', 'ordering_title': 'count_repentance', 'number': 7, 'active': True, 'editable': True},
    'total_tithe': {
        'id': 0, 'title': 'Десятины', 'ordering_title': 'tithe', 'number': 8, 'active': True, 'editable': True},
    'total_donations': {
        'id': 0, 'title': 'Пожертвования', 'ordering_title': 'donations', 'number': 9, 'active': True, 'editable': True},
    'total_pastor_tithe': {
        'id': 0, 'title': 'Десятина пастора', 'ordering_title': 'pastor_tithe', 'number': 10, 'active': True, 'editable': True},
    'transfer_payments': {
        'id': 0, 'title': '15% к перечислению', 'ordering_title': 'transfer_payments', 'number': 11, 'active': True, 'editable': True},
    'currency_donations': {
        'id': 0, 'title': 'Пожертвований в другой валюте', 'ordering_title': 'currency_donations', 'number': 12, 'active': True, 'editable': True},
    'value': {
        'id': 0, 'title': 'Сумма', 'ordering_title': 'value', 'number': 13, 'active': True, 'editable': True},
    'action': {
        'id': 0, 'title': 'Действие', 'ordering_title': 'payment_status', 'number': 14, 'active': True, 'editable': True},
}

deal_columns = {
    'full_name': {
        'id': 0, 'title': 'ФИО', 'ordering_title': 'partnership__user__last_name', 'number': 1, 'active': True, 'editable': False},
    'date_created': {
        'id': 0, 'title': 'Дата сделки', 'ordering_title': 'date_created', 'number': 2, 'active': True, 'editable': True},
    'responsible': {
        'id': 0, 'title': 'Менеджер', 'ordering_title': 'responsible__last_name', 'number': 3, 'active': True, 'editable': True},
    'sum': {
        'id': 0, 'title': 'Сумма', 'ordering_title': 'value', 'number': 4, 'active': True, 'editable': True},
    'type': {
        'id': 0, 'title': 'Тип сделки', 'ordering_title': 'type', 'number': 5, 'active': True, 'editable': True},
    'action': {
        'id': 0, 'title': 'Действие', 'ordering_title': 'done', 'number': 6, 'active': True, 'editable': True},
    'done': {
        'id': 0, 'title': 'Закрыта', 'ordering_title': 'done', 'number': 7, 'active': True, 'editable': True},
}

deal_payment_columns = {
    'purpose_fio': {
        'id': 0, 'title': 'Плательщик', 'ordering_title': 'deals__partnership__user__last_name', 'number': 1, 'active': True, 'editable': False},
    'sum_str': {
        'id': 0, 'title': 'Сумма', 'ordering_title': 'sum', 'number': 2, 'active': True, 'editable': True},
    'manager': {
        'id': 0, 'title': 'Супервайзер', 'ordering_title': 'manager__last_name', 'number': 3, 'active': True, 'editable': True},
    'description': {
        'id': 0, 'title': 'Примечание', 'ordering_title': 'description', 'number': 4, 'active': True, 'editable': True},
    'sent_date': {
        'id': 0, 'title': 'Дата поступления', 'ordering_title': 'sent_date', 'number': 5, 'active': True, 'editable': True},
    'purpose_date': {
        'id': 0, 'title': 'Дата сделки', 'ordering_title': 'deals__date_created', 'number': 6, 'active': True, 'editable': True},
    'purpose_manager_fio': {
        'id': 0, 'title': 'Менеджер', 'ordering_title': 'deals__responsible__last_name', 'number': 7, 'active': True, 'editable': True},
    'created_at': {
        'id': 0, 'title': 'Дата создания', 'ordering_title': 'created_at', 'number': 8, 'active': True, 'editable': True},
    'purpose_type': {
        'id': 0, 'title': 'Тип сделки', 'ordering_title': 'deals__type', 'number': 9, 'active': True, 'editable': True},
}

meeting_summary_columns = {
    'owner': {
        'id': 0, 'title': 'Лидер', 'ordering_title': 'last_name', 'number': 1, 'active': True, 'editable': False},
    'master': {
        'id': 0, 'title': 'Ответственный', 'ordering_title': 'master__last_name', 'number': 2, 'active': True, 'editable': True},
    'meetings_submitted': {
        'id': 0, 'title': 'Заполненные отчеты', 'ordering_title': 'meetings_submitted', 'number': 3, 'active': True, 'editable': True},
    'meetings_in_progress': {
        'id': 0, 'title': 'Отчеты к заполнению', 'ordering_title': 'meetings_in_progress', 'number': 4, 'active': True, 'editable': True},
    'meetings_expired': {
        'id': 0, 'title': 'Просроченные отчеты', 'ordering_title': 'meetings_expired', 'number': 5, 'active': True, 'editable': True},
}

report_summary_columns = {
    'pastor': {
        'id': 0, 'title': 'Пастор', 'ordering_title': 'last_name', 'number': 1, 'active': True, 'editable': False},
    'master': {
        'id': 0, 'title': 'Ответственный', 'ordering_title': 'master__last_name', 'number': 2, 'active': True, 'editable': True},
    'reports_submitted': {
        'id': 0, 'title': 'Заполненные отчеты', 'ordering_title': 'reports_submitted', 'number': 3, 'active': True, 'editable': True},
    'reports_in_progress': {
        'id': 0, 'title': 'Отчеты к заполнению', 'ordering_title': 'reports_in_progress', 'number': 4, 'active': True, 'editable': True},
    'reports_expired': {
        'id': 0, 'title': 'Просроченные отчеты', 'ordering_title': 'reports_expired', 'number': 5, 'active': True, 'editable': True},
}

partner_summary_columns = {
    'manager': {
        'id': 0, 'title': 'Менеджер', 'ordering_title': 'manager', 'number': 1, 'active': True, 'editable': False},
    'plan': {
        'id': 0, 'title': 'План', 'ordering_title': 'plan', 'number': 2, 'active': True, 'editable': True},
    'potential_sum': {
        'id': 0, 'title': 'Потенциал', 'ordering_title': 'potential_sum', 'number': 3, 'active': True, 'editable': True},
    'sum_deals': {
        'id': 0, 'title': 'Сумма сделок', 'ordering_title': 'sum_deals', 'number': 4, 'active': True, 'editable': True},
    'percent_of_plan': {
        'id': 0, 'title': '% выполнения плана', 'ordering_title': 'percent_of_plan', 'number': 5, 'active': True, 'editable': True},
    'total_partners': {
        'id': 0, 'title': 'Всего партнеров', 'ordering_title': 'total_partners', 'number': 6, 'active': True, 'editable': True},
    'active_partners': {
        'id': 0, 'title': 'Активных партнеров', 'ordering_title': 'active_partners', 'number': 7, 'active': True, 'editable': True},
    'not_active_partners': {
        'id': 0, 'title': 'Неактивных партнеров', 'ordering_title': 'not_active_partners', 'number': 8, 'active': True, 'editable': True},
    'sum_pay': {
        'id': 0, 'title': 'Сумма партнерских', 'ordering_title': 'sum_pay', 'number': 9, 'active': True, 'editable': True},
    'sum_pay_tithe': {
        'id': 0, 'title': 'Сумма десятин', 'ordering_title': 'sum_pay_tithe', 'number': 10, 'active': True, 'editable': True},
    'total_sum': {
        'id': 0, 'title': 'Общая сумма', 'ordering_title': 'total_sum', 'number': 11, 'active': True, 'editable': True},
}

report_payment_columns = {
    'church': {
        'id': 0, 'title': 'Церковь', 'ordering_title': 'church_reports__church__title', 'number': 1, 'active': True, 'editable': False},
    'sum_str': {
        'id': 0, 'title': 'Сумма', 'ordering_title': 'sum', 'number': 2, 'active': True, 'editable': True},
    'manager': {
        'id': 0, 'title': 'Менеджер', 'ordering_title': 'manager__last_name', 'number': 3, 'active': True, 'editable': True},
    'description': {
        'id': 0, 'title': 'Примечание', 'ordering_title': 'description', 'number': 4, 'active': True, 'editable': True},
    'sent_date': {
        'id': 0, 'title': 'Дата поступления', 'ordering_title': 'sent_date', 'number': 5, 'active': True, 'editable': True},
    'report_date': {
        'id': 0, 'title': 'Дата подачи отчета', 'ordering_title': 'church_reports__date', 'number': 6, 'active': True, 'editable': True},
    'pastor_fio': {
        'id': 0, 'title': 'Пастор', 'ordering_title': 'church_reports__church__pastor__last_name', 'number': 7, 'active': True, 'editable': True},
    'created_at': {
        'id': 0, 'title': 'Дата создания', 'ordering_title': 'created_at', 'number': 8, 'active': True, 'editable': True},
}

task_columns = {
    'date_published': {
        'id': 0, 'title': 'Дата', 'ordering_title': 'date_published', 'number': 1, 'active': True, 'editable': True},
    'type': {
        'id': 0, 'title': 'Тип', 'ordering_title': 'type', 'number': 2, 'active': True, 'editable': True},
    'creator': {
        'id': 0, 'title': 'Автор', 'ordering_title': 'creator__last_name', 'number': 3, 'active': True, 'editable': True},
    'executor': {
        'id': 0, 'title': 'Исполнитель', 'ordering_title': 'executor__last_name', 'number': 4, 'active': True, 'editable': True},
    'division': {
        'id': 0, 'title': 'Депортамент', 'ordering_title': 'division__title', 'number': 5, 'active': True, 'editable': True},
    'target': {
        'id': 0, 'title': 'Объект', 'ordering_title': 'target__last_name', 'number': 6, 'active': True, 'editable': True},
    'description': {
        'id': 0, 'title': 'Описание', 'ordering_title': 'description', 'number': 7, 'active': True, 'editable': True},
    'status': {
        'id': 0, 'title': 'Статус', 'ordering_title': 'status', 'number': 8, 'active': True, 'editable': True},
    'finish_report': {
        'id': 0, 'title': 'Комментарий', 'ordering_title': 'finish_report', 'number': 9, 'active': True, 'editable': True},
    'date_finish': {
        'id': 0, 'title': 'Дата закрытия', 'ordering_title': 'date_finish', 'number': 10, 'active': True, 'editable': True},
}

group_user_columns = {
    'fullname': {
        'id': 0, 'title': 'ФИО', 'ordering_title': 'last_name', 'number': 1, 'active': True, 'editable': True},
    'phone_number': {
        'id': 0, 'title': 'Номер телефона', 'ordering_title': 'phone_number', 'number': 2, 'active': True, 'editable': True},
    'repentance_date': {
        'id': 0, 'title': 'Дата Покаяния', 'ordering_title': 'repentance_date', 'number': 3, 'active': True, 'editable': True},
    'spiritual_level': {
        'id': 0, 'title': 'Духовный уровень', 'ordering_title': 'spiritual_level', 'number': 4, 'active': True, 'editable': True},
    'born_date': {
        'id': 0, 'title': 'Дата рождения', 'ordering_title': 'born_date', 'number': 5, 'active': True, 'editable': True},
}

summit_stats_columns = {
    'attended': {
        'id': 0, 'title': 'Присутствие', 'ordering_title': 'attended', 'number': 1, 'active': True, 'editable': False},
    'full_name': {
        'id': 0, 'title': 'ФИО', 'ordering_title': 'last_name', 'number': 2, 'active': True, 'editable': False},
    'responsible': {
        'id': 0, 'title': 'Ответственный', 'ordering_title': 'responsible', 'number': 3, 'active': True, 'editable': True},
    'phone_number': {
        'id': 0, 'title': 'Номер телефона', 'ordering_title': 'user__phone_number', 'number': 4, 'active': True, 'editable': True},
    'code': {
        'id': 0, 'title': 'Номер билета', 'ordering_title': 'code', 'number': 5, 'active': True, 'editable': True},
    'department': {
        'id': 0, 'title': 'Отдел', 'ordering_title': 'department', 'number': 6, 'active': True, 'editable': True},
}

TABLES = {
    'home_group': home_group_columns,
    'deal': deal_columns,
    'deal_payment': deal_payment_columns,
    'meeting': meeting_columns,
    'meeting_summary': meeting_summary_columns,
    'report_summary': report_summary_columns,
    'report_payment': report_payment_columns,
    'task': task_columns,
    'partner_summary': partner_summary_columns,
    'user': user_columns,
    'partner': partner_columns,
    'church_partner': church_partner_columns,
    'summit': summit_columns,

    'church': church_columns,
    'attend': attend_columns,
    'church_report': church_report_columns,
    'group_user': group_user_columns,
    'summit_stats': summit_stats_columns,
}


def get_table(table_name, user):
    from apps.navigation.api.serializers import RedisTableSerializer
    user = user.id if isinstance(user, CustomUser) else user

    columns = deepcopy(TABLES.get(table_name, {}))
    user_columns = RedisTableSerializer({'name': table_name, 'user_id': user}).data.get('columns', {})
    for name in columns:
        if name in user_columns:
            columns[name]['active'] = user_columns[name]['active']
            columns[name]['number'] = user_columns[name]['number']
    column_list = sorted(list(columns.items()), key=lambda a: a[1]['number'])
    columns = OrderedDict()
    for field, attributes in column_list:
        columns[field] = attributes
    return columns
