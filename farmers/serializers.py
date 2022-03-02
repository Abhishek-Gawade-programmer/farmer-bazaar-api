from rest_framework import serializers
from items.models import Item
from items.serializers import ItemImageSerializer


class ShortItemStatisticSerializer(serializers.ModelSerializer):
    title_image = serializers.SerializerMethodField(read_only=True)
    category = serializers.CharField(source="category.name")
    category_type = serializers.CharField(source="category_type.name")
    sub_category = serializers.CharField(source="sub_category.name")
    # no_of_items_placed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Item
        fields = ("id", "title_image", "category", "category_type", "sub_category")

    def get_title_image(self, obj):
        image_list = ItemImageSerializer(obj.images.all()[0]).data
        return image_list
# def get_no_of_items_placed(self, obj):
#     return
