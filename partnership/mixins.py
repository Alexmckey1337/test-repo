from _pydecimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Sum, Case, When, IntegerField, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from common.views_mixins import ExportViewSetMixin
from partnership.models import Partnership, Deal
from partnership.permissions import CanSeePartnerStatistics, CanCreatePartnerPayment, CanSeeDealPayments, \
    CanExportPartnerList
from payment.models import Payment, Currency
from payment.views_mixins import CreatePaymentMixin, ListPaymentMixin


class PartnerStatMixin:
    @list_route(methods=['get'], permission_classes=(IsAuthenticated, CanSeePartnerStatistics))
    def stats_payments(self, request):
        current_partner = get_object_or_404(Partnership, user=request.user)

        self.check_stats_permissions(current_partner)

        deals = self.get_deals_of_partner(request, current_partner)
        deals = self.filter_deals_by_month(request, deals)
        # deals = Deal.objects.all()  # for test, del this
        stats = dict()

        deals_with_sum = deals.annotate_total_sum()

        stats['deals'] = self.stats_by_deals(deals, deals_with_sum)
        stats['partners'] = self.stats_by_partners(deals, deals_with_sum)
        stats['sum'] = self.stats_by_sum(deals, deals_with_sum)

        return Response(stats)

    @list_route(methods=['get'], renderer_classes=(TemplateHTMLRenderer,),
                permission_classes=(IsAuthenticated, CanSeePartnerStatistics))
    def stat_deals(self, request):
        current_partner = get_object_or_404(Partnership, user=request.user)

        self.check_stats_permissions(current_partner)

        deals = self.get_deals_of_partner(request, current_partner)
        deals = self.filter_deals_by_month(request, deals)
        deals = deals.base_queryset(). \
            annotate_full_name(). \
            annotate_responsible_name(). \
            annotate_total_sum(). \
            order_by('-date_created', 'id')
        #
        # serializer = DealSerializer(deals, many=True)

        return Response({'deals': deals}, template_name='partner/partials/stat_deals.html')

    @list_route(methods=['get'], renderer_classes=(TemplateHTMLRenderer,),
                permission_classes=(IsAuthenticated, CanSeePartnerStatistics))
    def stat_payments(self, request):
        current_partner = get_object_or_404(Partnership, user=request.user)

        self.check_stats_permissions(current_partner)

        deals = self.get_deals_of_partner(request, current_partner)
        deals = self.filter_deals_by_month(request, deals)
        deals_ids = set(deals.values_list('id', flat=True))
        content_type = ContentType.objects.get_for_model(Deal)
        payments = Payment.objects.filter(
            content_type=content_type, object_id__in=deals_ids)
        #
        # serializer = PaymentShowSerializer(payments, many=True)

        return Response({'payments': payments}, template_name='partner/partials/stat_payments.html')

    # Helpers

    @staticmethod
    def check_stats_permissions(current_partner):
        if current_partner.level > Partnership.MANAGER:
            raise PermissionDenied({'detail': _('Статистику можно просматривать только менеджерам.')})

    @staticmethod
    def get_deals_of_partner(request, current_partner):
        request_partner_id = request.query_params.get('partner_id')

        if current_partner.level == Partnership.MANAGER or not request_partner_id:
            return current_partner.disciples_deals
        if request_partner_id == 'all':
            return Deal.objects.filter(responsible__isnull=False)
        partner = get_object_or_404(Partnership, id=request_partner_id)
        return partner.disciples_deals

    @staticmethod
    def filter_deals_by_month(request, deals):
        month = request.query_params.get('month', timezone.now().month)
        year = request.query_params.get('year', timezone.now().year)

        return deals.filter(date_created__month=month, date_created__year=year)

    @staticmethod
    def stats_by_deals(deals, deals_with_sum):
        paid = deals_with_sum.filter(total_sum__gte=F('value')).count()
        unpaid = deals_with_sum.filter(total_sum__lt=F('value'), total_sum=Decimal(0)).count()
        partial_paid = deals_with_sum.filter(total_sum__lt=F('value'), total_sum__gt=Decimal(0)).count()
        deals_result = {
            'paid_count': paid,
            'unpaid_count': unpaid,
            'partial_paid_count': partial_paid
        }

        closed_count = deals.aggregate(
            closed_count=Sum(
                Case(When(done=True, then=1), default=0,
                     output_field=IntegerField())
            ),
            unclosed_count=Sum(
                Case(When(done=False, then=1), default=0,
                     output_field=IntegerField())
            ))
        deals_result.update(closed_count)

        return deals_result

    @staticmethod
    def stats_by_partners(deals, deals_with_sum):
        paid = set(deals_with_sum.filter(total_sum__gte=F('value')).aggregate(p=ArrayAgg('partnership'))['p'])
        unpaid = set(deals_with_sum.filter(
            total_sum__lt=F('value'),
            total_sum=Decimal(0)).aggregate(p=ArrayAgg('partnership'))['p'])
        partial_paid = set(deals_with_sum.filter(
            total_sum__lt=F('value'),
            total_sum__gt=Decimal(0)).aggregate(p=ArrayAgg('partnership'))['p'])
        paid_count = len(paid - unpaid - partial_paid)
        unpaid_count = len(unpaid - partial_paid - paid)
        partial_paid_count = len(partial_paid | (paid & unpaid))

        closed = set(deals.filter(done=True).aggregate(p=ArrayAgg('partnership'))['p'])
        unclosed = set(deals.filter(done=False).aggregate(p=ArrayAgg('partnership'))['p'])
        closed_count = len(closed - unclosed)
        unclosed_count = len(unclosed)

        return {
            'paid_count': paid_count,
            'unpaid_count': unpaid_count,
            'partial_paid_count': partial_paid_count,
            'closed_count': closed_count,
            'unclosed_count': unclosed_count
        }

    @staticmethod
    def stats_by_sum(deals, deals_with_sum):
        sum = dict()
        currencies = set(
            deals.aggregate(currency_codes=ArrayAgg('currency__code'))['currency_codes'])

        for c in Currency.objects.filter(code__in=currencies):
            total_paid_sum = deals_with_sum.filter(currency=c).aggregate(
                sum_planed=Coalesce(Sum('value'), Value(0)),
                sum_paid=Coalesce(Sum('total_sum'), Value(0)))
            closed_paid_sum = deals_with_sum.filter(currency=c, done=True).aggregate(
                sum_planed=Coalesce(Sum('value'), Value(0)),
                sum_paid=Coalesce(Sum('total_sum'), Value(0)))
            sum[c.code] = {
                'currency_name': c.name,
                'total_paid_sum': total_paid_sum,
                'closed_paid_sum': closed_paid_sum
            }
        return sum


class DealCreatePaymentMixin(CreatePaymentMixin):
    @detail_route(methods=['post'], permission_classes=(IsAuthenticated, CanCreatePartnerPayment))
    def create_payment(self, request, pk=None):
        return self._create_payment(request, pk)


class DealListPaymentMixin(ListPaymentMixin):
    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, CanSeeDealPayments))
    def payments(self, request, pk=None):
        return self._payments(request, pk)


class PartnerExportViewSetMixin(ExportViewSetMixin):
    @list_route(methods=['post'], permission_classes=(IsAuthenticated, CanExportPartnerList,))
    def export(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)
