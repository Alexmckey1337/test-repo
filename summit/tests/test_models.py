# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from account.factories import UserFactory


@pytest.mark.django_db
class TestSummitType:
    summit_title = 'Test Summit'
    club_name = 'Team Dream'

    def test__str__(self, summit_type):
        assert summit_type.__str__() == self.summit_title

    def test_image_url_without_image(self, summit_type):
        assert summit_type.image_url == ''

    def test_image_url_with_image(self, summit_type):
        summit_type.image = 'summit_type/images/test.jpg'
        assert summit_type.image_url == '/media/summit_type/images/test.jpg'


@pytest.mark.django_db
class TestSummit:
    summit_title = 'Test Summit'
    club_name = 'Team Dream'

    def test__str__(self, summit):
        assert summit.__str__() == '{} {}'.format(self.summit_title, summit.start_date)

    def test_consultants(self):
        # TODO write later
        pass

    def test_title(self, summit):
        assert summit.title == self.summit_title

    def test_club_name(self, summit):
        assert summit.club_name == self.club_name

    def test_without_special_cost(self, summit):
        summit.clean()

    def test_with_equal_costs(self, summit):
        with pytest.raises(ValidationError):
            summit.special_cost = Decimal('200')
            summit.save()
            summit.clean()

    def test_with_full_cost_less_then_special_cost(self, summit):
        with pytest.raises(ValidationError):
            summit.special_cost = Decimal('202')
            summit.save()
            summit.clean()

    def test_with_full_cost_more_then_special_cost(self, summit):
        summit.special_cost = Decimal('198')
        summit.save()
        summit.clean()


@pytest.mark.django_db
class TestAnket:
    summit_title = 'Test Summit'
    club_name = 'Team Dream'

    def test__str__(self, anket, summit, user):
        assert anket.__str__() == '{} {} {}'.format(
            user.fullname, self.summit_title, summit.start_date)

    def test_is_full_paid_for_member_true(self, summit, anket, payment_factory):
        special_cost = Decimal('100')
        summit.special_cost = special_cost
        summit.save()

        anket.visited = True
        anket.save()

        payment = payment_factory(purpose=anket, sum=special_cost, currency_sum=summit.currency)

        assert anket.is_full_paid

        payment.sum = special_cost + Decimal('10')
        payment.save()

        assert anket.is_full_paid

    def test_is_full_paid_for_member_false(self, summit, anket, payment_factory):
        special_cost = Decimal('100')
        summit.special_cost = special_cost
        summit.save()

        anket.visited = True
        anket.save()

        payment_factory(purpose=anket, sum=special_cost - Decimal('10'), currency_sum=summit.currency)

        assert not anket.is_full_paid

    def test_is_full_paid_for_non_member_true(self, summit, anket, payment_factory):
        full_cost = summit.full_cost

        anket.visited = False
        anket.save()

        payment = payment_factory(purpose=anket, sum=full_cost, currency_sum=summit.currency)

        assert anket.is_full_paid

        payment.sum = full_cost + Decimal('10')
        payment.save()

        assert anket.is_full_paid

    def test_is_full_paid_for_non_member_false(self, summit, anket, payment_factory):
        full_cost = summit.full_cost

        anket.visited = False
        anket.save()

        payment_factory(purpose=anket, sum=full_cost - Decimal('10'), currency_sum=summit.currency)

        assert not anket.is_full_paid

    def test_is_member_true(self, summit_factory, summit_anket_factory, user, anket, summit):
        other_summit = summit_factory(
            type=summit.type,
            start_date=date(1998, 11, 22),
            end_date=date(1998, 11, 26),
            full_cost=Decimal('20'),
        )
        summit_anket_factory(user=user, summit=other_summit, visited=True)
        assert anket.is_member

    def test_is_member_false(self, summit_factory, summit_anket_factory, user, anket, summit):
        other_summit = summit_factory(
            start_date=date(1998, 11, 22),
            end_date=date(1998, 11, 26),
            full_cost=Decimal('20'),
        )
        summit_anket_factory(user=user, summit=other_summit, visited=False)
        assert not anket.is_member

    def test_currency(self, currency_factory, summit, anket):
        currency = currency_factory(code='cur', short_name='curr')
        summit.currency = currency
        summit.save()

        assert anket.currency == summit.currency


@pytest.mark.django_db
class TestAnketEmail:
    def test__str__(self, anket_email, anket):
        assert anket_email.__str__() == '{}: {}'.format(anket_email.created_at, anket)


@pytest.mark.django_db
class TestSummitLesson:
    def test__str__(self, lesson, summit):
        assert lesson.__str__() == '{}: {}'.format(summit, lesson.name)


@pytest.mark.django_db
class TestSummitUserConsultant:
    def test__str__(self, summit_uc, summit, anket):
        assert summit_uc.__str__() == '{}: {} is consultant for {}'.format(
            summit, summit_uc.consultant, anket)

    def test_other_summit_user(self, summit_uc, summit_anket_factory):
        summit_uc.user = summit_anket_factory()

        with pytest.raises(ValidationError):
            summit_uc.clean()

    def test_other_summit_consultant(self, summit_uc, summit_anket_factory):
        summit_uc.consultant = summit_anket_factory()

        with pytest.raises(ValidationError):
            summit_uc.clean()


@pytest.mark.django_db
class TestAnketNote:
    def test__str__with_long_text(self, anket_note_factory):
        note = anket_note_factory(text='t' * 51)
        assert note.__str__() == note.short_text

    def test__str__with_50_length_text(self, anket_note_factory):
        note = anket_note_factory(text='t' * 50)
        assert note.__str__() == note.short_text

    def test__str__with_short_text(self, anket_note_factory):
        note = anket_note_factory(text='t' * 20)
        assert note.__str__() == note.short_text

    def test_short_text_with_long_text(self, anket_note_factory):
        note = anket_note_factory(text='t' * 51)
        assert note.short_text == '{}...'.format('t' * 47)

    def test_short_text_with_50_length_text(self, anket_note_factory):
        note = anket_note_factory(text='t' * 50)
        assert note.short_text == 't' * 50

    def test_short_text_with_short_text(self, anket_note_factory):
        note = anket_note_factory(text='t' * 20)
        assert note.short_text == 't' * 20

    def test_owner_name(self, anket_note_factory):
        owner = UserFactory()
        note = anket_note_factory(owner=owner)

        assert note.owner_name == owner.fullname


@pytest.mark.django_db
class TestSummitTicket:
    summit_title = 'Test Summit'

    def test__str__(self, ticket, summit):
        assert ticket.__str__() == '{summit}: {title} (progress)'.format(summit=summit, title=ticket.title)

    def test_get_absolute_url(self, ticket):
        assert ticket.get_absolute_url() == '/summits/tickets/{}/'.format(ticket.pk)
