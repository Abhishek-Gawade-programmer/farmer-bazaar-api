from django_filters import rest_framework as filters
from .models import Item, CategoryType


class ItemFilter(filters.FilterSet):
    """
    FILTERING ON
        -title(case insensitive)
        -category(name)
        -category_type(name)
        -quantity(int)
    """

    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    category = filters.CharFilter(field_name="category__name")
    sub_category = filters.CharFilter(field_name="sub_category__name")
    category_type = filters.CharFilter(field_name="category_type__name")
    quantity = filters.NumberFilter(field_name="quantity", lookup_expr="lte")

    class Meta:
        model = Item
        fields = ["title", "category", "sub_category", "category_type", "quantity_unit"]


class CategoryTypeFilter(filters.FilterSet):
    """
    FILTERING ON
        -name(case insensitive)
        -category(name)
    """

    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    category = filters.CharFilter(
        field_name="category__name",
    )

    class Meta:
        model = CategoryType
        fields = ["name", "category"]
