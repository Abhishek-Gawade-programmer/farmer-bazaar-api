from django_filters import rest_framework as filters
from .models import Item


class ItemFilter(filters.FilterSet):

    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    category = filters.CharFilter(field_name="category__name")

    class Meta:
        model = Item
        fields = ["title", "category"]
