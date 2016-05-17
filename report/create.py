from account.models import CustomUser as User
from report.models import WeekReport, MonthReport, YearReport, UserReport
from datetime import date


def months(user_id):
    try:
        master = User.objects.get(id=user_id)
        try:
            master_month_report = MonthReport.objects.get(user=master.user_report, date__month=date.today().month)
            return "This user has already a report fot this month"
        except MonthReport.DoesNotExist:
            pass
        master_month_report = MonthReport.objects.create(user=master.user_report, date=date.today())
        disciples = User.objects.filter(master=master).all()
        for disciple in disciples.all():
            try:
                disciple_month_report = MonthReport.objects.get(user=disciple.user_report,
                                                                date__month=date.today().month)
                print "This user has already a report fot this month"
                continue
            except MonthReport.DoesNotExist:
                pass
            disciple_month_report = MonthReport.objects.create(user=disciple.user_report, date=date.today())
            disciples_of_disciple = User.objects.filter(master=disciple).all()
            for disciple_of_disciple in disciples_of_disciple.all():
                try:
                    disciple_of_disciple_month_report = MonthReport.objects.get(user=disciple_of_disciple.user_report,
                                                                                date__month=date.today().month)
                    print "This user has already a report fot this month"
                    continue
                except MonthReport.DoesNotExist:
                    pass
                disciple_of_disciple_month_report = MonthReport.objects.create(user=disciple_of_disciple.user_report,
                                                                               date=date.today())
    except User.DoesNotExist:
        return u"No fucking user"
    return u"I'm done"


def years(user_id):
    try:
        master = User.objects.get(id=user_id)
        try:
            master_month_report = YearReport.objects.get(user=master.user_report, date__year=date.today().year)
            return u"This user has already a report fot this month"
        except YearReport.DoesNotExist:
            pass
        master_month_report = YearReport.objects.create(user=master.user_report, date=date.today())
        disciples = User.objects.filter(master=master).all()
        for disciple in disciples.all():
            try:
                disciple_month_report = YearReport.objects.get(user=disciple.user_report,
                                                               date__year=date.today().year)
                print u"This user has already a report fot this month"
                continue
            except YearReport.DoesNotExist:
                pass
            disciple_month_report = YearReport.objects.create(user=disciple.user_report, date=date.today())
            disciples_of_disciple = User.objects.filter(master=disciple).all()
            for disciple_of_disciple in disciples_of_disciple.all():
                try:
                    disciple_of_disciple_month_report = YearReport.objects.get(user=disciple_of_disciple.user_report,
                                                                               date__year=date.today().year)
                    print u"This user has already a report fot this year"
                    continue
                except YearReport.DoesNotExist:
                    pass
                disciple_of_disciple_month_report = YearReport.objects.create(user=disciple_of_disciple.user_report,
                                                                              date=date.today())
    except User.DoesNotExist:
        return u"No fucking user"
    return u"I'm done"


def user_reports():
    from report.models import UserReport
    from account.models import CustomUser as User
    users = User.objects.all()
    i = 0
    for user in users.all():
        try:
            user_report = UserReport.objects.get(user=user)
        except UserReport.DoesNotExist:
            user_report = UserReport.objects.create(user=user)
            i += 1
    print "Created %i user reports" % i
    return None


def check(id):
    ur = UserReport.objects.get(user__id=id)
    w = WeekReport.objects.filter(user=ur).last()
    w.get_stat()
    print "home_count %i" % w.home_count
    print "home_value %i" % w.home_value
    print "home_as_leader_count %i" % w.home_as_leader_count
    print "home_as_leader_value %i" % w.home_as_leader_value
    print "night_count %i" % w.night_count
    print "night_as_leader_count %i" % w.night_as_leader_count
    print "service_count %i" % w.service_count
    print "service_as_leader_count %i" % w.service_as_leader_count


def create_months():
    user_reports = UserReport.objects.all()
    for user_report in user_reports.all():
        try:
            month_report = MonthReport.objects.get(user=user_report, date__month=date.today().month)
            return "This user has already a report fot this month"
        except MonthReport.DoesNotExist:
            month_report = MonthReport.objects.create(user=user_report, date=date.today())
    return "Month reports: OK"


def create_years():
    user_reports = UserReport.objects.all()
    for user_report in user_reports.all():
        try:
            year_report = YearReport.objects.get(user=user_report, date__year=date.today().year)
            return "This user has already a report fot this year"
        except YearReport.DoesNotExist:
            year_report = YearReport.objects.create(user=user_report, date=date.today())
    return "Year reports: OK"