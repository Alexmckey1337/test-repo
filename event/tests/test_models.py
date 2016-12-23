# -*- coding: utf-8
from __future__ import unicode_literals

from django.test import TestCase

from event.factories import MeetingTypeFactory, MeetingFactory, MeetingAttendFactory


class TestMeetingType(TestCase):
    def setUp(self):
        self.meeting_type = MeetingTypeFactory()

    def test__str__(self):
        self.assertEqual(
            self.meeting_type.__str__(),
            self.meeting_type.name
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.meeting_type.get_absolute_url(),
            '/meeting_types/{}/'.format(self.meeting_type.code)
        )


class TestMeeting(TestCase):
    def setUp(self):
        self.meeting = MeetingFactory()

    def test__str__(self):
        self.assertEqual(
            self.meeting.__str__(),
            '{}: {}'.format(self.meeting.type.name, self.meeting.date.strftime('%d %B %Y'))
        )


class TestMeetingAttend(TestCase):
    def setUp(self):
        self.meeting_attend = MeetingAttendFactory()

    def test__str__(self):
        self.assertEqual(
            self.meeting_attend.__str__(),
            '[ ] {} — visitor of {}'.format(self.meeting_attend.user, self.meeting_attend.meeting)
        )
        self.meeting_attend.attended = True
        self.meeting_attend.save()
        self.assertEqual(
            self.meeting_attend.__str__(),
            '[X] {} — visitor of {}'.format(self.meeting_attend.user, self.meeting_attend.meeting)
        )
