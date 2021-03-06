import pytest


@pytest.mark.django_db
class TestStatus:
    def test__str__(self, status):
        assert status.__str__() == status.title


@pytest.mark.django_db
class TestDivision:
    def test__str__(self, division):
        assert division.__str__() == division.title
