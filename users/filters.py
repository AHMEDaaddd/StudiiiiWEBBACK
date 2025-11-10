import django_filters

from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    # фильтрация по связанным id
    course = django_filters.NumberFilter(
        field_name="course__id",
        lookup_expr="exact",
    )
    lesson = django_filters.NumberFilter(
        field_name="lesson__id",
        lookup_expr="exact",
    )
    method = django_filters.CharFilter(
        field_name="method",
        lookup_expr="exact",
    )
    # фильтрация по дате (от / до)
    paid_at__gte = django_filters.IsoDateTimeFilter(
        field_name="paid_at",
        lookup_expr="gte",
    )
    paid_at__lte = django_filters.IsoDateTimeFilter(
        field_name="paid_at",
        lookup_expr="lte",
    )

    class Meta:
        model = Payment
        fields = ["course", "lesson", "method", "paid_at__gte", "paid_at__lte"]
