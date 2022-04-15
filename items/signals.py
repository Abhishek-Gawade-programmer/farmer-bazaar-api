from django.db.models.signals import pre_save, post_save, post_delete
from .models import ItemBag, Item


def item_bag_pre_save(sender, created, instance, **kwargs):
    if created:
        print("Creating th item bag so item can sell")
        instance.item.can_able_to_sell = True
        instance.item.save()


post_save.connect(item_bag_pre_save, sender=ItemBag)


def item_post_save(sender, created, instance, **kwargs):
    if not created:
        print("checking the item bag status ")
        for item_bag in instance.bags.all():
            if item_bag.convert_quantity_kg() > instance.convert_quantity_kg():
                print("Convertind available status to FALSE")
                item_bag.available_status = False
            else:
                print("Convertind available status to TRUE")
                item_bag.available_status = True
            item_bag.save()


post_save.connect(item_post_save, sender=Item)
