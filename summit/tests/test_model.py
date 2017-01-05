# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from account.factories import UserFactory
from payment.factories import CurrencyFactory
from summit.factories import SummitTypeFactory, SummitFactory, SummitAnketFactory, AnketEmailFactory, \
    SummitLessonFactory, SummitUserConsultantFactory, AnketNoteFactory


class TestSummitType(TestCase):
    def setUp(self):
        self.summit_title = 'Test Summit'
        self.club_name = 'Team Dream'

        self.summit_type = SummitTypeFactory()

    def test__str__(self):
        self.assertEqual(
            self.summit_type.__str__(),
            self.summit_title
        )

    def test_image_url_without_image(self):
        self.assertEqual(self.summit_type.image_url, '')

    def test_image_url_with_image(self):
        self.summit_type.image = 'summit_type/images/test.jpg'
        self.assertEqual(self.summit_type.image_url, '/media/summit_type/images/test.jpg')


class TestSummit(TestCase):
    def setUp(self):
        self.summit_title = 'Test Summit'
        self.club_name = 'Team Dream'

        self.summit = SummitFactory(full_cost=Decimal('222'))

    def test__str__(self):
        self.assertEqual(
            self.summit.__str__(),
            '{} {}'.format(self.summit_title, self.summit.start_date)
        )

    def test_consultants(self):
        # TODO write later
        pass

    def test_title(self):
        self.assertEqual(self.summit.title, self.summit_title)

    def test_club_name(self):
        self.assertEqual(self.summit.club_name, self.club_name)

    def test_without_special_cost(self):
        self.summit.clean()

    def test_with_equal_costs(self):
        with self.assertRaises(ValidationError):
            self.summit.special_cost = Decimal('222')
            self.summit.save()
            self.summit.clean()

    def test_with_full_cost_less_then_special_cost(self):
        with self.assertRaises(ValidationError):
            self.summit.special_cost = Decimal('224')
            self.summit.save()
            self.summit.clean()

    def test_with_full_cost_more_then_special_cost(self):
        self.summit.special_cost = Decimal('220')
        self.summit.save()
        self.summit.clean()


class TestAnket(TestCase):
    def setUp(self):
        self.summit_title = 'Test Summit'
        self.club_name = 'Team Dream'

        self.user = UserFactory()
        self.summit = SummitFactory()
        self.anket = SummitAnketFactory(user=self.user, summit=self.summit)

    def test__str__(self):
        self.assertEqual(
            self.anket.__str__(),
            '{} {} {}'.format(self.anket.user.fullname, self.summit_title, self.summit.start_date)
        )

    def test_is_member_true(self):
        other_summit = SummitFactory(
            type=self.summit.type,
            start_date=date(1998, 11, 22),
            end_date=date(1998, 11, 26),
            full_cost=Decimal('20'),
        )
        SummitAnketFactory(user=self.user, summit=other_summit, visited=True)
        self.assertTrue(self.anket.is_member)

    def test_is_member_false(self):
        other_summit = SummitFactory(
            start_date=date(1998, 11, 22),
            end_date=date(1998, 11, 26),
            full_cost=Decimal('20'),
        )
        SummitAnketFactory(user=self.user, summit=other_summit, visited=False)
        self.assertFalse(self.anket.is_member)

    def test_is_full_paid_for_member_true(self):
        special_cost = Decimal('100')
        self.summit.special_cost = special_cost
        self.summit.save()

        self.anket.visited = True
        self.anket.value = special_cost
        self.anket.save()

        self.assertTrue(self.anket.is_full_paid)

        self.anket.value = special_cost + Decimal('10')
        self.anket.save()

        self.assertTrue(self.anket.is_full_paid)

    def test_is_full_paid_for_member_false(self):
        special_cost = Decimal('100')
        self.summit.special_cost = special_cost
        self.summit.save()

        self.anket.visited = True
        self.anket.value = special_cost - Decimal('10')
        self.anket.save()

        self.assertFalse(self.anket.is_full_paid)

    def test_is_full_paid_for_non_member_true(self):
        full_cost = self.summit.full_cost

        self.anket.visited = False
        self.anket.value = full_cost
        self.anket.save()

        self.assertTrue(self.anket.is_full_paid)

        self.anket.value = full_cost + Decimal('10')
        self.anket.save()

        self.assertTrue(self.anket.is_full_paid)

    def test_is_full_paid_for_non_member_false(self):
        full_cost = self.summit.full_cost

        self.anket.visited = False
        self.anket.value = full_cost - Decimal('10')
        self.anket.save()

        self.assertFalse(self.anket.is_full_paid)

    def test_currency(self):
        currency = CurrencyFactory(code='cur', short_name='curr')
        self.summit.currency = currency
        self.summit.save()

        self.assertEqual(self.anket.currency, self.summit.currency)


class TestAnketEmail(TestCase):
    def setUp(self):
        self.anket = SummitAnketFactory()
        self.anket_email = AnketEmailFactory(anket=self.anket)

    def test__str__(self):
        self.assertEqual(
            self.anket_email.__str__(),
            '{}: {}'.format(self.anket_email.created_at, self.anket)
        )


class TestSummitLesson(TestCase):
    def setUp(self):
        self.lesson = SummitLessonFactory()

    def test__str__(self):
        self.assertEqual(
            self.lesson.__str__(),
            '{}: {}'.format(self.lesson.summit, self.lesson.name)
        )


class TestSummitUserConsultant(TestCase):
    def setUp(self):
        self.summit_uc = SummitUserConsultantFactory()

    def test__str__(self):
        self.assertEqual(
            self.summit_uc.__str__(),
            '{}: {} is consultant for {}'.format(
                self.summit_uc.summit, self.summit_uc.consultant, self.summit_uc.user)
        )

    def test_other_summit_user(self):
        self.summit_uc.user = SummitAnketFactory()

        with self.assertRaises(ValidationError):
            self.summit_uc.clean()

    def test_other_summit_consultant(self):
        self.summit_uc.consultant = SummitAnketFactory()

        with self.assertRaises(ValidationError):
            self.summit_uc.clean()


class TestAnketNote(TestCase):
    def setUp(self):
        self.note = AnketNoteFactory()

    def test__str__with_long_text(self):
        note = AnketNoteFactory(text='t' * 51)
        self.assertEqual(note.__str__(), note.short_text)

    def test__str__with_50_length_text(self):
        note = AnketNoteFactory(text='t' * 50)
        self.assertEqual(note.__str__(), note.short_text)

    def test__str__with_short_text(self):
        note = AnketNoteFactory(text='t' * 20)
        self.assertEqual(note.__str__(), note.short_text)

    def test_short_text_with_long_text(self):
        note = AnketNoteFactory(text='t' * 51)
        self.assertEqual(
            note.short_text,
            '{}...'.format('t' * 47)
        )

    def test_short_text_with_50_length_text(self):
        note = AnketNoteFactory(text='t' * 50)
        self.assertEqual(note.short_text, 't' * 50)

    def test_short_text_with_short_text(self):
        note = AnketNoteFactory(text='t' * 20)
        self.assertEqual(note.short_text, 't' * 20)

    def test_owner_name(self):
        owner = UserFactory()
        note = AnketNoteFactory(owner=owner)

        self.assertEqual(note.owner_name, owner.fullname)
