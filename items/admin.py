from django.contrib import admin
from .models import (
    ItemImage,
    Category,
    Item,
    ItemRating,
    ItemBag,
    SubCategory,
    SellerReply,
    CategoryType,
)

admin.site.register(ItemImage)
admin.site.register(Category)
admin.site.register(CategoryType)
admin.site.register(SubCategory)
admin.site.register(Item)
admin.site.register(ItemRating)
admin.site.register(SellerReply)
admin.site.register(ItemBag)
