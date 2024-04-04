from django.urls import path
from .views import upload_file, get_current_selection_state, confirm_list_of_students, get_applicants_list

urlpatterns = [
    path("current-selection-state", get_current_selection_state, name="current selection state"),
    path("upload", upload_file, name="upload file"),
    path("confirm-list", confirm_list_of_students, name="confirm list"),
    path("applicant-list", get_applicants_list, name="applicant list"),
]
