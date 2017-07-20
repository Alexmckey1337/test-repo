/**
 * Created by pluton on 29.06.17.
 */

const USER = {
    detail: (userId) => `/api/v1.1/users/${userId}/`,
    list: () => `/api/v1.1/users/`,
    short: () => `/api/v1.0/short_users/`,
    set_church: (userId) => `/api/v1.1/users/${userId}/set_church/`,
    set_home_group: (userId) => `/api/v1.1/users/${userId}/set_home_group/`,
    departments: (userId) => `/api/v1.1/users/${userId}/departments/`,
};

const SUMMIT = {
    users: (summitId) => `/api/v1.0/summits/${summitId}/users/`,
    stats: (summitId) => `/api/v1.0/summits/${summitId}/stats/`,
    report_by_bishop: (summitId) => `/api/v1.0/summit/${summitId}/report_by_bishops/`,
    master: (summitId) => `/api/v1.0/summit/${summitId}/master/`,
    bishop_high_masters: (summitId) => `/api/v1.0/summits/${summitId}/bishop_high_masters/`,
    attends: (summitId) => `/api/v1.0/summit/${summitId}/stats/attends/`,
};

const SUMMIT_PROFILE = {
    detail: (profileId) => `/api/v1.0/summit_profiles/${profileId}/`,
    list: () => `/api/v1.0/summit_profiles/`,
    predelete: (profileId) => `/api/v1.0/summit_profiles/${profileId}/predelete/`,
    create_payment: (profileId) => `/api/v1.0/summit_profiles/${profileId}/create_payment/`,
    list_payments: (profileId) => `/api/v1.0/summit_profiles/${profileId}/payments/`,
    set_ticket_status: (profileId) => `/api/v1.0/summit_profiles/${profileId}/set_ticket_status/`,
    create_note: (profileId) => `/api/v1.0/summit_profiles/${profileId}/create_note/`,
};

const SUMMIT_LESSON = {
    detail: (lessonId) => `/api/v1.0/summit_lessons/${lessonId}/`,
    list: () => `/api/v1.0/summit_lessons/`,
    add_viewer: (lessonId) => `/api/v1.0/summit_lessons/${lessonId}/add_viewer/`,
    del_viewer: (lessonId) => `/api/v1.0/summit_lessons/${lessonId}/del_viewer/`,
};

const SUMMIT_TICKET = {
    users: (ticketId) => `/api/v1.0/summit_tickets/${ticketId}/users/`,
    print: (ticketId) => `/api/v1.0/summit_tickets/${ticketId}/print/`,
};

const HOME_MEETING = {
    list: (reportId) => `/api/v1.0/events/home_meetings/`,
    detail: (reportId) => `/api/v1.0/events/home_meetings/${reportId}/`,
    visitors: (reportId) => `/api/v1.0/events/home_meetings/${reportId}/visitors/`,
    submit: (reportId) => `/api/v1.0/events/home_meetings/${reportId}/submit/`,
    stats: () => `/api/v1.0/events/home_meetings/statistics/`,
    church_report: () => `/api/v1.0/events/church_reports/`,
};

const PARTNER = {
    detail: (partnerId) => `/api/v1.1/partnerships/${partnerId}/`,
    list: () => `/api/v1.1/partnerships/`,
    simple: () => `/api/v1.1/partnerships/simple/`,
    create_payment: (partnerId) => `/api/v1.1/partnerships/${partnerId}/create_payment/`,
    stats_payment: () => `/api/v1.1/partnerships/stats_payments/`,
    stats_deal: () => `/api/v1.1/partnerships/stat_deals/`,
    stat_payment: () => `/api/v1.1/partnerships/stat_payments/`,
    update_need: (partnerId) => `/api/v1.1/partnerships/${partnerId}/update_need/`,
};

const DEAL = {
    detail: (dealId) => `/api/v1.0/deals/${dealId}/`,
    list: () => `/api/v1.0/deals/`,
    payments: (dealId) => `/api/v1.0/deals/${dealId}/payments/`,
    create_payment: (dealId) => `/api/v1.0/deals/${dealId}/create_payment/`,
};

const CHURCH = {
    detail: (churchId) => `/api/v1.0/churches/${churchId}/`,
    list: () => `/api/v1.0/churches/`,
    users: (churchId) => `/api/v1.0/churches/${churchId}/users/`,
    stats: (churchId) => `/api/v1.0/churches/${churchId}/statistics/`,
    del_user: (churchId) => `/api/v1.0/churches/${churchId}/del_user/`,
    add_user: (churchId) => `/api/v1.0/churches/${churchId}/add_user/`,
    for_select: () => `/api/v1.0/churches/for_select/`,
    available_pastors: () => `/api/v1.0/churches/available_pastors/`,
    potential_users_church: () => `/api/v1.0/churches/potential_users_church/`,
    potential_users_group: (churchId) => `/api/v1.0/churches/${churchId}/potential_users_group/`,
};

const HOME_GROUP = {
    detail: (groupId) => `/api/v1.0/home_groups/${groupId}/`,
    list: () => `/api/v1.0/home_groups/`,
    users: (groupId) => `/api/v1.0/home_groups/${groupId}/users/`,
    stats: (groupId) => `/api/v1.0/home_groups/${groupId}/statistics/`,
    del_user: (groupId) => `/api/v1.0/home_groups/${groupId}/del_user/`,
    add_user: (groupId) => `/api/v1.0/home_groups/${groupId}/add_user/`,
    for_select: () => `/api/v1.0/home_groups/for_select/`,
    available_leaders: () => `/api/v1.0/home_groups/available_leaders/`,
};

const PAYMENT = {
    deals: () => `/api/v1.0/payments/deal/`
};

const URLS = {
    login: () => `/api/v1.0/login/`,
    logout: () => `/api/v1.0/logout/`,
    password_view: () => `/api/v1.0/password_view/`,
    password_forgot: () => `/api/v1.0/password_forgot/`,
    country: () => `/api/v1.0/countries/`,
    region: () => `/api/v1.0/regions/`,
    city: () => `/api/v1.0/cities/`,
    department: () => `/api/v1.0/departments/`,
    division: () => `/api/v1.0/divisions/`,
    hierarchy: () => `/api/v1.0/hierarchy/`,
    summit_search: () => `/api/v1.0/summit_search/`,
    notification: () => `/api/v1.0/notifications/today/`,
    update_columns: () => `/api/v1.0/update_columns/`,
    generate_summit_tickets: (summitId) => `/api/v1.0/generate_summit_tickets/${summitId}/`,
    profile_status: () => `/api/v1.0/summit_attends/anket_active_status/`,
    summit: SUMMIT,
    user: USER,
    partner: PARTNER,
    deal: DEAL,
    payment: PAYMENT,
    summit_profile: SUMMIT_PROFILE,
    summit_ticket: SUMMIT_TICKET,
    summit_lesson: SUMMIT_LESSON,
    home_meeting: HOME_MEETING,
    church: CHURCH,
    home_group: HOME_GROUP,
};
