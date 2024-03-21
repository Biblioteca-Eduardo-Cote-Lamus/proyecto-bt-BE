from django.urls import path
from .views import login, hasAccess

urlpatterns = [
    path("", login, name="login"),
    path("hasAccess", hasAccess, name="hasAccess"),
]
