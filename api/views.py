from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse


class ApiRoot(generics.GenericAPIView):
    name = "api-root"

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "login_user": reverse("token_obtain_pair", request=request),
                "user_register": reverse("user_register", request=request),
                "token_refresh": reverse("token_refresh", request=request),
            }
        )
