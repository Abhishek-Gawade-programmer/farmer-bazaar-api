from rest_framework import exceptions, permissions


USER_T_C_NOT_ACCEPTED = "User Don't have Accepted Terms And conditions"
CANT_ADD_RATINGS_OUR_ITEM = "You Can't Add Ratings On Your Item"
DONT_HAVE_ADMIN_PERMISSION = "You Don't Have Administrations Permission"


# Checks That Is Requested User Is Owner Of Item
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


# Checks That Is Requested User Is Same As To Edit Itembag Which Have It
class IsOwnerOfItemBelongs(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.item.user == request.user


# Checks That Is Requested User Is Same As To Edit Profile
class IsOwnerOfObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


# Checks That Is Requested User Is Same As To Edit Profile
class IsAbleToSellItem(permissions.BasePermission):
    message = USER_T_C_NOT_ACCEPTED

    def has_permission(self, request, view):
        return request.user.user_profile.can_able_to_sell_product()


# Checks The User Owner Of Order
class IsOwnerOfOrder(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.order.user == request.user


# Checks User Unable To Add Ratings On His/her Items
class IsUnableRatingItem(permissions.BasePermission):
    message = CANT_ADD_RATINGS_OUR_ITEM

    def has_object_permission(self, request, view, obj):
        return not (obj.user == request.user)


# Checks Whether User Admin User
class IsAdministerUser(permissions.BasePermission):
    message = DONT_HAVE_ADMIN_PERMISSION

    def has_permission(self, request, view):
        return request.user.user_profile.admin_access
