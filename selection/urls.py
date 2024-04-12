from django.urls import path
from .views import (
    upload_file,
    get_current_selection_state,
    confirm_list_of_students,
    get_applicants_list,
    check_register_form_state,
    check_if_user_can_send_form,
    check_schedule_file,
    register_user
)

urlpatterns = [
    path("current-selection-state",get_current_selection_state,name="current selection state",),
    path("upload", upload_file, name="upload file"),
    path("confirm-list", confirm_list_of_students, name="confirm list"),
    path("applicant-list", get_applicants_list, name="applicant list"),
    path("register-form-state", check_register_form_state, name="register form state"),
    path("check-user-form/<int:id>", check_if_user_can_send_form, name="Check if user can send form"),
    path( "check-schedule-file", check_schedule_file, name="Check if schedule file is valid",),
    path( "register-form", register_user, name=" Register user form",),
]
