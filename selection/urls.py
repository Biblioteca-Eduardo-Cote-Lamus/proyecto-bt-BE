from django.urls import path
from .views import (
    upload_file,
    get_current_selection_state,
    confirm_list_of_students,
    get_applicants_list,
    check_register_form_state,
    check_if_user_can_send_form,
    check_schedule_file,
    register_user,
    get_beca_current_state,
    extend_register_form_date,
    confirm_list_step2,
    ubication_assign,
    get_becas_by_ubication
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
    path( "check-current-state-beca/<int:id>", get_beca_current_state, name="Return the current beca state",),
    path( "extended-date-form", extend_register_form_date, name="Extended date of register form",),
    path( "confirm-register-form", confirm_list_step2, name="Update the current state selection and the current state of becas",),
    path( "ubication-assign", ubication_assign, name="Test the ubication assign",),
    path( "becas-selected-by-ubication", get_becas_by_ubication, name="Get the list of becas assigned by ubication",),
]
