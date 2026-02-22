import django_filters
from .models import Transaction

class TransactionFilter(django_filters.FilterSet):
    category_type = django_filters.CharFilter(field_name='category__type')

    class Meta:
        model = Transaction
        fields = ['category', 'date', 'category_type']