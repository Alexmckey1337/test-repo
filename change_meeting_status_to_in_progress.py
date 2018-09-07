from apps.event.models import Meeting

night_meetings = Meeting.objects.filter(status=3, date='2018-09-06')

for meeting in night_meetings:
    meeting.status = 1
    meeting.save()
