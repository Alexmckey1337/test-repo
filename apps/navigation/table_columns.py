from collections import OrderedDict
from copy import deepcopy
from typing import List


class Column:
    def __init__(self, name, title, ordering_title='', active=True, editable=True):
        self.name = name
        self.id = 0
        self.title = title
        self.ordering_title = ordering_title
        self.active = active
        self.editable = editable

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'ordering_title': self.ordering_title,
            'active': self.active,
            'editable': self.editable,
        }


class Table:
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = columns

    def to_dict(self):
        columns = {}
        for i, c in enumerate(self.columns):
            columns[c.name] = c.to_dict()
            columns[c.name]['number'] = i
        return columns


church_columns = Table('church', [
    Column('get_title', 'Название церкви', 'title', editable=False),
    Column('department', 'Отдел', 'department__title'),
    Column('city', 'Город', 'city'),
    Column('pastor', 'Пастор Церкви', 'pastor__last_name'),
    Column('is_open', 'Открыта', 'is_open'),
    Column('address', 'Адрес', 'address'),
    Column('phone_number', 'Телефонный номер', 'phone_number'),
    Column('website', 'Адрес сайта', 'website'),
    Column('country', 'Страна', 'country'),
    Column('opening_date', 'Дата открытия', 'opening_date'),
    Column('region', 'Область', 'region'),
    Column('stable_count', 'Количество стабильных'),
    Column('count_people', 'Количество людей'),
    Column('count_hg_people', 'Людей в домашних группах'),
    Column('count_home_groups', 'Количество домашних групп'),
    Column('locality', 'Населенный пункт'),
]).to_dict()

user_columns = Table('user', [
    Column('fullname', 'ФИО', 'last_name', editable=False),
    Column('email', 'Email', 'email'),
    Column('phone_number', 'Номер телефона', 'phone_number'),
    Column('born_date', 'Дата рождения', 'born_date'),
    Column('hierarchy', 'Иерархия', 'hierarchy__level'),
    Column('departments', 'Отдел', 'department_title'),
    Column('country', 'Страна', 'country'),
    Column('region', 'Область', 'region'),
    Column('city', 'Населенный пункт', 'city'),
    Column('district', 'Район', 'district'),
    Column('address', 'Адрес', 'address'),
    Column('social', 'Социальные сети', 'facebook'),
    Column('divisions', 'Служения', 'divisions'),
    Column('master', 'Ответственный', 'master__last_name'),
    Column('repentance_date', 'Дата покаяния', 'repentance_date'),
    Column('spiritual_level', 'Духовный уровень', 'spiritual_level'),
    Column('get_church', 'Церковь', ''),
    Column('locality', 'Населенный пункт', ''),
    Column('get_home_group', 'Домашняя Группа', ''),
]).to_dict()

partner_columns = Table('partner', [
    Column('user.fullname', 'ФИО', 'user__last_name', editable=False),
    Column('user.email', 'Email', 'user__email'),
    Column('user.phone_number', 'Номер телефона', 'user__phone_number'),
    Column('user.born_date', 'Дата рождения', 'user__born_date'),
    Column('user.hierarchy.title', 'Иерархия', 'user__hierarchy__level'),
    Column('user.departments', 'Отдел', 'user__department_title'),
    Column('user.country', 'Страна', 'user__country'),
    Column('user.region', 'Область', 'user__region'),
    Column('user.city', 'Населенный пункт', 'user__city'),
    Column('user.district', 'Район', 'user__district'),
    Column('user.address', 'Адрес', 'user__address'),
    Column('user.social', 'Социальные сети', 'user__facebook'),
    Column('user.divisions', 'Служения', 'user__divisions'),
    Column('user.master.fullname', 'Ответственный', 'user__master__last_name'),
    Column('user.repentance_date', 'Дата покаяния', 'user__repentance_date'),
    Column('user.spiritual_level', 'Духовный уровень', 'user__spiritual_level'),
    Column('user.get_church', 'Церковь', ''),
    Column('user.locality', 'Населенный пункт', ''),
    Column('group', 'Тег', 'group__title', editable=False),
    Column('responsible', 'Менеджер', 'responsible__last_name'),
    Column('value', 'Сумма', 'value'),
]).to_dict()

church_partner_columns = Table('church_partner', [
    Column('church.get_title', 'Название церкви', 'church__title', editable=False),
    Column('church.department.title', 'Отдел', 'church__department__title'),
    Column('church.city', 'Город', 'church__city'),
    Column('church.pastor.fullname', 'Пастор Церкви', 'church__pastor__last_name'),
    Column('church.is_open', 'Открыта', 'church__is_open'),
    Column('church.address', 'Адрес', 'church__address'),
    Column('church.phone_number', 'Телефонный номер', 'church__phone_number'),
    Column('church.website', 'Адрес сайта', 'church__website'),
    Column('church.country', 'Страна', 'church__country'),
    Column('church.opening_date', 'Дата открытия', 'church__opening_date'),
    Column('church.locality', 'Населенный пункт', ''),
    Column('group', 'Тег', 'group__title', editable=False),
    Column('responsible', 'Менеджер', 'responsible__last_name'),
    Column('value', 'Сумма', 'value'),
]).to_dict()

home_group_columns = Table('home_group', [
    Column('get_title', 'Название Группы', 'title', editable=False),
    Column('church', 'Церковь', 'church__title'),
    Column('city', 'Город', 'city'),
    Column('leader', 'Лидер', 'leader__last_name'),
    Column('opening_date', 'Дата открытия', 'opening_date'),
    Column('address', 'Адрес', 'address'),
    Column('phone_number', 'Телефонный номер', 'phone_number'),
    Column('website', 'Адрес сайта', 'website'),
    Column('count_users', 'Количество людей', 'count_users'),
    Column('locality', 'Населенный пункт', ''),
]).to_dict()

summit_columns = Table('summit', [
    Column('full_name', 'ФИО', 'last_name'),
    Column('author', 'Автор регистрации', 'author__last_name'),
    Column('spiritual_level', 'Духовный уровень', 'spiritual_level'),
    Column('divisions_title', 'Служения', 'divisions_title'),
    Column('department', 'Отдел', 'department'),
    Column('hierarchy_title', 'Иерархия', 'hierarchy_level'),
    Column('phone_number', 'Номер телефона', 'user__phone_number'),
    Column('email', 'Email', 'user__email'),
    Column('social', 'Социальные сети', 'user__facebook'),
    Column('country', 'Страна', 'country'),
    Column('city', 'Населенный пункт', 'city'),
    Column('region', 'Область', 'user__region'),
    Column('district', 'Район', 'user__district'),
    Column('address', 'Адрес', 'user__address'),
    Column('born_date', 'Дата рождения', 'user__born_date'),
    Column('repentance_date', 'Дата Покаяния', 'user__repentance_date'),
    Column('code', 'Код', 'code'),
    Column('value', 'Оплата', 'value'),
    Column('description', 'Примечания', 'description'),
    Column('ticket_status', 'Статус билета', 'ticket_status'),
    Column('e_ticket', 'Электронный билет', 'status__reg_code_requested'),
    Column('has_email', 'Email отправлен', 'has_email'),
    Column('responsible', 'Ответственный', 'responsible'),
    Column('action', 'Действие', 'done'),
]).to_dict()

meeting_columns = Table('meeting', [
    Column('id', '№', 'id', editable=False),
    Column('home_group', 'Домашняя группа', 'home_group__title'),
    Column('owner', 'Лидер домашней группы', 'owner__last_name'),
    Column('phone_number', 'Телефонный номер', 'home_group__phone_number'),
    Column('type', 'Тип отчета', 'type__code'),
    Column('visitors_attended', 'Присутствовали', 'visitors_attended'),
    Column('visitors_absent', 'Отсутствовали', 'visitors_absent'),
    Column('guest_count', 'Гостей', 'guest_count'),
    Column('new_count', 'Новых', 'new_count'),
    Column('repentance_count', 'Покаяний', 'repentance_count'),
    Column('total_sum', 'Сумма пожертвований', 'total_sum'),
    Column('date', 'Дата создания', 'date'),
]).to_dict()

attend_columns = Table('attend', [
    Column('attended', 'Присутствие', 'attended'),
    Column('user', 'ФИО', 'user__last_name', editable=False),
    Column('spiritual_level', 'Духовный уровень', 'user__spiritual_level'),
    Column('phone_number', 'Телефонный номер', 'user__phone_number'),
    Column('note', 'Коментарий', 'note'),
]).to_dict()

church_report_columns = Table('church_report', [
    Column('id', '№', 'id', editable=False),
    Column('date', 'Дата создания', 'date'),
    Column('church', 'Церковь', 'church__title'),
    Column('pastor', 'Пастор Церкви', 'pastor__last_name'),
    Column('total_peoples', 'Людей на собрании', 'count_people'),
    Column('total_new_peoples', 'Новых людей', 'new_people'),
    Column('total_repentance', 'Покаяний', 'count_repentance'),
    Column('total_tithe', 'Десятины', 'tithe'),
    Column('total_donations', 'Пожертвования', 'donations'),
    Column('total_pastor_tithe', 'Десятина пастора', 'pastor_tithe'),
    Column('transfer_payments', '15% к перечислению', 'transfer_payments'),
    Column('currency_donations', 'Пожертвований в другой валюте', 'currency_donations'),
    Column('value', 'Сумма', 'value'),
    Column('action', 'Действие', 'payment_status'),
]).to_dict()

deal_columns = Table('deal', [
    Column('full_name', 'ФИО', 'partnership__user__last_name', editable=False),
    Column('date_created', 'Дата сделки', 'date_created'),
    Column('responsible', 'Менеджер', 'responsible__last_name'),
    Column('sum', 'Сумма', 'value'),
    Column('type', 'Тип сделки', 'type'),
    Column('action', 'Действие', 'done'),
]).to_dict()

deal_payment_columns = Table('deal_payment', [
    Column('purpose_fio', 'Плательщик', 'deals__partnership__user__last_name', editable=False),
    Column('sum_str', 'Сумма', 'sum'),
    Column('manager', 'Супервайзер', 'manager__last_name'),
    Column('description', 'Примечание', 'description'),
    Column('sent_date', 'Дата поступления', 'sent_date'),
    Column('purpose_date', 'Дата сделки', 'deals__date_created'),
    Column('purpose_manager_fio', 'Менеджер', 'deals__responsible__last_name'),
    Column('created_at', 'Дата создания', 'created_at'),
    Column('purpose_type', 'Тип сделки', 'deals__type'),
]).to_dict()

meeting_summary_columns = Table('meeting_summary', [
    Column('owner', 'Лидер', 'last_name', editable=False),
    Column('master', 'Ответственный', 'master__last_name'),
    Column('meetings_submitted', 'Заполненные отчеты', 'meetings_submitted'),
    Column('meetings_in_progress', 'Отчеты к заполнению', 'meetings_in_progress'),
    Column('meetings_expired', 'Просроченные отчеты', 'meetings_expired'),
]).to_dict()

report_summary_columns = Table('report_summary', [
    Column('pastor', 'Пастор', 'last_name', editable=False),
    Column('master', 'Ответственный', 'master__last_name'),
    Column('reports_submitted', 'Заполненные отчеты', 'reports_submitted'),
    Column('reports_in_progress', 'Отчеты к заполнению', 'reports_in_progress'),
    Column('reports_expired', 'Просроченные отчеты', 'reports_expired'),
]).to_dict()

partner_summary_columns = Table('partner_summary', [
    Column('manager', 'Менеджер', 'manager', editable=False),
    Column('plan', 'План', 'plan'),
    Column('potential_sum', 'Потенциал', 'potential_sum'),
    Column('sum_deals', 'Сумма сделок', 'sum_deals'),
    Column('percent_of_plan', '% выполнения плана', 'percent_of_plan'),
    Column('total_partners', 'Всего партнеров (активные/неактивные)', 'total_partners'),
    Column('sum_pay', 'Сумма партнерских', 'sum_pay'),
    Column('sum_pay_tithe', 'Сумма десятин', 'sum_pay_tithe'),
    Column('sum_pay_church', 'Сумма по церквям', 'sum_pay_church'),
    Column('total_sum', 'Общая сумма', 'total_sum'),
]).to_dict()

report_payment_columns = Table('report_payment', [
    Column('church', 'Церковь', 'church_reports__church__title', editable=False),
    Column('sum_str', 'Сумма', 'sum'),
    Column('manager', 'Менеджер', 'manager__last_name'),
    Column('description', 'Примечание', 'description'),
    Column('sent_date', 'Дата поступления', 'sent_date'),
    Column('report_date', 'Дата подачи отчета', 'church_reports__date'),
    Column('pastor_fio', 'Пастор', 'church_reports__church__pastor__last_name'),
    Column('created_at', 'Дата создания', 'created_at'),
]).to_dict()

task_columns = Table('task', [
    Column('date_published', 'Дата', 'date_published'),
    Column('type', 'Тип', 'type'),
    Column('creator', 'Автор', 'creator__last_name'),
    Column('executor', 'Исполнитель', 'executor__last_name'),
    Column('division', 'Депортамент', 'division__title'),
    Column('target', 'Объект', 'target__last_name'),
    Column('description', 'Описание', 'description'),
    Column('status', 'Статус', 'status'),
    Column('finish_report', 'Комментарий', 'finish_report'),
    Column('date_finish', 'Дата закрытия', 'date_finish'),
]).to_dict()

group_user_columns = Table('group_user', [
    Column('fullname', 'ФИО', 'last_name'),
    Column('phone_number', 'Номер телефона', 'phone_number'),
    Column('repentance_date', 'Дата Покаяния', 'repentance_date'),
    Column('spiritual_level', 'Духовный уровень', 'spiritual_level'),
    Column('born_date', 'Дата рождения', 'born_date'),
]).to_dict()

summit_stats_columns = Table('summit_stats', [
    Column('attended', 'Присутствие', 'attended', editable=False),
    Column('full_name', 'ФИО', 'last_name', editable=False),
    Column('author', 'Автор регистрации', 'author__last_name'),
    Column('phone_number', 'Номер телефона', 'user__phone_number'),
    Column('code', 'Номер билета', 'code'),
    Column('department', 'Отдел', 'department'),
    Column('responsible', 'Ответственный', 'responsible'),
]).to_dict()

unstable_user_columns = Table('summit_stats', [
    Column('full_name', 'ФИО', editable=False),
    Column('phone_number', 'Номер телефона'),
    Column('master_name', 'Ответственный'),
    Column('sex', 'Пол'),
    Column('hierarchy', 'Иерархия'),
    Column('departments', 'Отделы'),
    Column('group_name', 'Домашняя группа'),
    Column('country_name', 'Страна'),
    Column('city_name', 'Город'),
    Column('church_name', 'Церковь'),
    Column('repentance_date', 'Дата покаяния'),
]).to_dict()

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
    'unstable_user': unstable_user_columns,
}


def get_table(table_name, user):
    from apps.account.models import CustomUser
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
