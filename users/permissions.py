from rest_framework import permissions


# checks that is requested user is owner of item
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


# checks that is requested user is same as to edit profile
class IsSameUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


# # checks that is requested user is same as to edit profile
# class IsAbleToSellItem(permissions.BasePermission):
#     def has_permission(self, request, view):
#         # print(obj)
#         print(request, view)
#         if request.method == "POST":
#             return request.user.user_profile.can_able_to_sell_product()
#         return False
