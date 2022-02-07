from rest_framework import exceptions, permissions

# messages user terms conditions not accepted
USER_T_C_NOT_ACCEPTED = "User Don't have Accepted Terms And conditions"


# checks that is requested user is owner of item
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


# checks that is requested user is same as to edit itembag which have it
class IsOwnerOfItemBelongs(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.item.user == request.user


# checks that is requested user is same as to edit profile
class IsOwnerOfObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


# checks that is requested user is same as to edit profile
class IsAbleToSellItem(permissions.BasePermission):
    message = USER_T_C_NOT_ACCEPTED

    def has_permission(self, request, view):
        return request.user.user_profile.can_able_to_sell_product()
