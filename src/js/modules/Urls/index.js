'use strict';

const USER = {
    detail: (userId) => `/api/users/${userId}/`,
    list: () => `/api/users/`,
    short: () => `/api/short_users/`,
    set_church: (userId) => `/api/users/${userId}/set_church/`,
    set_home_group: (userId) => `/api/users/${userId}/set_home_group/`,
    departments: (userId) => `/api/users/${userId}/departments/`,
    dashboard_count: () => `/api/users/dashboard_counts/`,
    list_user: () => `/api/users/for_select/`,
    find_duplicates: () => `/api/users/duplicates_avoided/`,
    short_for_dashboard: () => `/api/dashboard_users/`,
    set_partner_role: (id) => `/api/users/${id}/set_partner_role/`,
    update_partner_role: (id) => `/api/users/${id}/update_partner_role/`,
    delete_partner_role: (id) => `/api/users/${id}/delete_partner_role/`,
    managers: () => `/api/users/partner_managers/`,
};

const CONTROLS = {
    bd_access: () => `/api/controls/db_access/`,
    bd_access_submit: () => `/api/controls/db_access/submit/`,
    password_submit: (id) => `/api/controls/db_access/${id}/`
}

const SUMMIT = {
    users: (summitId) => `/api/summits/${summitId}/users/`,
    stats: (summitId) => `/api/summits/${summitId}/stats/`,
    report_by_bishop: (summitId) => `/api/summit/${summitId}/report_by_bishops/`,
    master: (summitId) => `/api/summit/${summitId}/master/`,
    bishop_high_masters: (summitId) => `/api/summits/${summitId}/bishop_high_masters/`,
    attends: (summitId) => `/api/summit/${summitId}/stats/attends/`,
    stats_by_master: (summitId, masterId) => `/api/summit/${summitId}/stats/master/${masterId}/disciples/`,
    stats_latecomer: (summitId) => `/api/summit/${summitId}/stats/latecomers/`,
    send_codes: (summitId) => `/api/summit/${summitId}/send_unsent_codes/`,
    send_schedules: (summitId) => `/api/summit/${summitId}/send_unsent_schedules/`,
    send_code: (anketId) => `/api/summit/profile/${anketId}/send_code/?method=email`,
};

const SUMMIT_PROFILE = {
    detail: (profileId) => `/api/summit_profiles/${profileId}/`,
    list: () => `/api/summit_profiles/`,
    predelete: (profileId) => `/api/summit_profiles/${profileId}/predelete/`,
    create_payment: (profileId) => `/api/summit_profiles/${profileId}/create_payment/`,
    list_payments: (profileId) => `/api/summit_profiles/${profileId}/payments/`,
    set_ticket_status: (profileId) => `/api/summit_profiles/${profileId}/set_ticket_status/`,
    create_note: (profileId) => `/api/summit_profiles/${profileId}/create_note/`,
};

const SUMMIT_LESSON = {
    detail: (lessonId) => `/api/summit_lessons/${lessonId}/`,
    list: () => `/api/summit_lessons/`,
    add_viewer: (lessonId) => `/api/summit_lessons/${lessonId}/add_viewer/`,
    del_viewer: (lessonId) => `/api/summit_lessons/${lessonId}/del_viewer/`,
};

const SUMMIT_TICKET = {
    users: (ticketId) => `/api/summit_tickets/${ticketId}/users/`,
    print: (ticketId) => `/api/summit_tickets/${ticketId}/print/`,
};

const CHURCH_REPORT = {
    list: () => `/api/events/church_reports/`,
    detail: (reportId) => `/api/events/church_reports/${reportId}/`,
    submit: (reportId) => `/api/events/church_reports/${reportId}/submit/`,
    stats: () => `/api/events/church_reports/statistics/`,
    statistics: () => `/api/events/church_reports/stats/`,
    dashboard_count: () => `/api/events/church_reports/dashboard_counts/`,
    summary: () => `/api/events/church_reports/reports_summary/`,
    create_payment: (reportId) => `/api/events/church_reports/${reportId}/create_payment/`,
    create_uah_payment: (reportId) => `/api/events/church_reports/${reportId}/create_uah_payment/`,
    payments: (id) => `/api/events/church_reports/${id}/payments/`,
    deals: () => `/api/payments/church_report/`,
};

const HOME_MEETING = {

    list: (reportId) => `/api/events/home_meetings/`,
    detail: (reportId) => `/api/events/home_meetings/${reportId}/`,
    visitors: (reportId) => `/api/events/home_meetings/${reportId}/visitors/`,
    submit: (reportId) => `/api/events/home_meetings/${reportId}/submit/`,
    stats: () => `/api/events/home_meetings/statistics/`,
    dashboard_count: () => `/api/events/home_meetings/dashboard_counts/`,
    summary: () => `/api/events/home_meetings/meetings_summary/`,
};

const EVENT = {
    home_meeting: HOME_MEETING,
    church_report: CHURCH_REPORT,
};

const PARTNER = {
    detail: (partnerId) => `/api/partnerships/${partnerId}/`,
    list: () => `/api/partnerships/`,
    church_detail: (partnerId) => `/api/church_partners/${partnerId}/`,
    church_list: () => `/api/church_partners/`,
    create_payment: (partnerId) => `/api/partnerships/${partnerId}/create_payment/`,
    stats_payment: () => `/api/partnerships/stats_payments/`,
    stats_deal: () => `/api/partnerships/stat_deals/`,
    stat_payment: () => `/api/partnerships/stat_payments/`,
    update_need: (partnerId) => `/api/partnerships/${partnerId}/update_need/`,
    managers_summary: () => `/api/partnerships/managers_summary/`,
    manager_summary: (id) => `/api/partnerships/${id}/manager_summary/`,
    set_managers_plan: (id) => `/api/partnerships/${id}/set_plan/`,
    last_deals: (id) => `/api/partners/${id}/last_deals/`,
    last_payments: (id) => `/api/partners/${id}/last_payments/`,
    church_last_deals: (id) => `/api/church_partners/${id}/last_deals/`,
    church_last_payments: (id) => `/api/church_partners/${id}/last_payments/`,
};

const DEAL = {
    detail: (dealId) => `/api/deals/${dealId}/`,
    list: () => `/api/deals/`,
    payments: (dealId) => `/api/deals/${dealId}/payments/`,
    create_payment: (dealId) => `/api/deals/${dealId}/create_payment/`,
    create_uah_payment: (dealId) => `/api/deals/${dealId}/create_uah_payment/`,
    find_duplicates: () => `/api/deals/get_duplicates/`,
    check_duplicates: () => `/api/deals/check_duplicates/`,
};

const CHURCH_DEAL = {
    detail: (dealId) => `/api/church_deals/${dealId}/`,
    list: () => `/api/church_deals/`,
    payments: (dealId) => `/api/church_deals/${dealId}/payments/`,
    create_payment: (dealId) => `/api/church_deals/${dealId}/create_payment/`,
    create_uah_payment: (dealId) => `/api/church_deals/${dealId}/create_uah_payment/`,
    find_duplicates: () => `/api/church_deals/get_duplicates/`,
    check_duplicates: () => `/api/church_deals/check_duplicates/`,
};
const CHURCH = {
    detail: (churchId) => `/api/churches/${churchId}/`,
    list: () => `/api/churches/`,
    users: (churchId) => `/api/churches/${churchId}/users/`,
    stats: (churchId) => `/api/churches/${churchId}/statistics/`,
    del_user: (churchId) => `/api/churches/${churchId}/del_user/`,
    add_user: (churchId) => `/api/churches/${churchId}/add_user/`,
    for_select: () => `/api/churches/for_select/`,
    available_pastors: () => `/api/churches/available_pastors/`,
    potential_users_church: () => `/api/churches/potential_users_church/`,
    potential_users_group: (churchId) => `/api/churches/${churchId}/potential_users_group/`,
    dashboard_count: () => `/api/churches/dashboard_counts/`,
    create_report: (id) => `/api/churches/${id}/create_report/`
};

const HOME_GROUP = {
    detail: (groupId) => `/api/home_groups/${groupId}/`,
    list: () => `/api/home_groups/`,
    users: (groupId) => `/api/home_groups/${groupId}/users/`,
    stats: (groupId) => `/api/home_groups/${groupId}/statistics/`,
    del_user: (groupId) => `/api/home_groups/${groupId}/del_user/`,
    add_user: (groupId) => `/api/home_groups/${groupId}/add_user/`,
    for_select: () => `/api/home_groups/for_select/`,
    leaders: () => `/api/home_groups/leaders/`,
    potential_leaders: () => `/api/home_groups/potential_leaders/`,
    create_report: (id) => `/api/home_groups/${id}/create_report/`
};

const PAYMENT = {
    deals: () => `/api/payments/deal/`,
    edit_payment: (id) => `/api/payments/${id}/`,
    payment_detail: (id) => `/api/payments/${id}/detail/`,
    supervisors: () => `/api/payments/supervisors/`,
};

const EXPORT = {
    partners: () => `/api/partnerships/export/`,
    church_partners: () => `/api/church_partners/export/`,
};

const PHONE = {

    list: () => `/api/all_calls/`,
    user: () => `/api/asterisk_users/`,
    changeUser: () => `/api/change_asterisk_user/`,
    lastThree: (id) => `/api/calls_to_user/?user_id=${id}&range=last_3`,
    filterMonth: (id, date) => `/api/calls_to_user/?user_id=${id}&range=month&month_date=${date}`,
    // detail: (reportId) => `/api/events/home_meetings/${reportId}/`,
    play: (file) => `http://192.168.240.47:7000/file/?file_name=${file}`,
};

const URLS = {
    login: () => `/api/login/`,
    logout: () => `/api/logout/`,
    password_view: () => `/api/password_view/`,
    password_forgot: () => `/api/password_forgot/`,
    country: () => `/api/countries/`,
    region: () => `/api/regions/`,
    city: () => `/api/cities/`,
    department: () => `/api/departments/`,
    division: () => `/api/divisions/`,
    hierarchy: () => `/api/hierarchy/`,
    summit_search: () => `/api/summit_search/`,
    notification_tickets: () => `/api/notifications/tickets/`,
    users_birthdays: () => `/api/notifications/birthdays/`,
    users_repentance_days: () => `/api/notifications/repentance/`,
    update_columns: () => `/api/update_columns/`,
    generate_summit_tickets: (summitId) => `/api/generate_summit_tickets/${summitId}/`,
    profile_status: () => `/api/summit_attends/anket_active_status/`,
    exports: () => `/api/notifications/exports/`,
    scan_code: () => `/api/summit_attends/accept_mobile_code`,
    summit: SUMMIT,
    controls: CONTROLS,
    user: USER,
    partner: PARTNER,
    deal: DEAL,
    church_deal: CHURCH_DEAL,
    payment: PAYMENT,
    summit_profile: SUMMIT_PROFILE,
    summit_ticket: SUMMIT_TICKET,
    summit_lesson: SUMMIT_LESSON,
    event: EVENT,
    church: CHURCH,
    home_group: HOME_GROUP,
    phone: PHONE,
    export: EXPORT,
};

export default URLS;
