import pytest


@pytest.mark.django_db
class TestDecimalWithCurrencyField:
    @pytest.mark.xfail
    def test__init__with_currency_field(self, decimal_with_currency_field):
        field = decimal_with_currency_field(currency_field='test_currency')
        assert field.currency_field == 'test_currency'

    @pytest.mark.xfail
    def test__init__without_currency_field(self, decimal_with_currency_field):
        field = decimal_with_currency_field()
        assert field.currency_field == 'currency'

    @pytest.mark.xfail
    def test_get_attribute(self, decimal_with_currency_field, currency):
        field = decimal_with_currency_field()
        instance = type('TestClass', (), {'currency': currency})
        assert field.get_attribute(instance) == (120, '{value} {short_name}', currency.output_dict())

    @pytest.mark.xfail
    def test_to_representation(self, decimal_with_currency_field):
        field = decimal_with_currency_field()
        value = (111, '{value} {short_name}', {'short_name': 'cur.'})
        assert field.to_representation(value) == '111 cur.'
