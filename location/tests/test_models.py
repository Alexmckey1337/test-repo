# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest


@pytest.mark.django_db
class TestCountry:
    def test__str__(self, country):
        assert country.__str__() == country.title


@pytest.mark.django_db
class TestRegion:
    def test__str__(self, region):
        assert region.__str__() == region.title


@pytest.mark.django_db
class TestCity:
    def test__str__(self, city):
        assert city.__str__() == city.title
