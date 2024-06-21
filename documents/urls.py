from django.contrib import admin
from django.urls import path
from .views import DocumentView

urlpatterns = [
    path('', DocumentView.as_view(), name='document-list-create')
]