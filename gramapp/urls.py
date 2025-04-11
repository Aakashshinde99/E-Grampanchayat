from django.urls import path
from . import views
from .views import tax_page, payment_success
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.conf.urls.i18n import i18n_patterns
from . import views



urlpatterns = [

    ############################################# User related all functions #####################################################
    path('debug-language/', views.debug_language, name='debug_language'),

    # path('', views.welcomePage, name='welcomePage'),
    ################### Home Page ############################
    path('', views.home_view, name='home_view'),

    ################### Language Selector ############################
    path("switch-language/<str:lang_code>/", views.switch_language, name="switch_language"),
    
    ################## User  functions #############################
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register_view'),
    path('user-dashboard/', views.dashboard_view, name='dashboard_view'),
    path('user-profile/', views.user_profile, name='user_profile'),

    ################## Water & Tax functions #############################
    path('tax', views.tax_page, name='tax'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path("download-receipt/<str:payment_id>/", views.generate_tax_receipt, name="download_tax_receipt"),

    ################### Certificates ############################
    path(_('certificates/'), views.certificates_page, name='certificates_page'),
    path(_('certificates/birth-certificate/'), views.apply_birth_certificate, name='apply_birth_certificate'),
    path(_('certificates/death-certificate/'), views.apply_death_certificate, name='apply_death_certificate'),
    path(_('certificates/marriage-certificate/'), views.apply_marriage_certificate, name='apply_marriage_certificate'),
    path(_('certificates/domicile-certificate/'), views.apply_domicile_certificate, name='apply_domicile_certificate'),
    
    path('my-certificate/<str:cert_type>/<int:cert_id>/view/', views.download_certificate, name='download_certificate'),


    ################## Shramdan & Abhiyaans ############################
    path('shramdan/', views.shramdan_page, name='shramdan_page'),

    ################## Gram Sabha Meetings ############################
    path('sabhameet', views.sabha_meetings_page, name='sabha_meetings_page'),

    #################### Health and Educational Services ################
    path('healthedu/', views.health_education_page, name='health_education_page'),

    ###################### Helpdesk ############################
    path('helpdesk/', views.helpdesk_page, name='helpdesk_page'),

    ################# Surveys ######################
    path('surveys/', views.surveys, name='surveys'),
    path('ongoing/', views.surveys_ongoing, name='surveys_ongoing'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('results/', views.survey_results, name='survey_results'),
    path('survey/<int:survey_id>/', views.survey_detail, name='survey_detail'),

    #################### Events ############################
    path('events', views.events, name='events'),

    #################### Photo Gallery ############################
    path('gallery/', views.user_gallery, name='user_gallery'),

    #################### Village Dashboard ############################
    path('village_dashboard/',
         views.village_dashboard,
         name='village_dashboard'),

    #################### Panchayat Profiles ############################
    path('panchayat-profile',
         views.panchayat_profile,
         name='panchayat_profile'),

    #################### Job Opportunities ############################
    path("jobs/", views.user_job_opportunities, name="user_job_opportunities"),

    #################### Tourism ############################
    path("tourism/", views.user_tourism, name="user_tourism"),

    #################### Notifications ############################
    path("notifications/", views.get_notifications, name="get_notifications"),
    path("notifications/mark-read/", views.mark_notifications_as_read, name="mark_notifications_read"),

    ############################################# Staff related all functions #####################################################
    path('staff-login/', views.staff_login, name='staff_login'),
    path('staff-logout/', views.staff_logout, name='staff_logout'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff-profile/', views.staff_profile, name='staff_profile'),
    
    ###################### Tax Management ############################
    path("staff/tax-management/", views.tax_management, name="tax_management"),
    path("staff/add-tax/", views.add_tax, name="add_tax"),
    path("staff/edit-tax/<int:tax_id>/", views.edit_tax, name="edit_tax"),

    ###################### Meetings Management ############################
    path("staff/meetings/", views.manage_meetings, name="manage_meetings"),
    path("staff/meetings/add/", views.add_meeting, name="add_meeting"),
    path("staff/meetings/delete/<int:meeting_id>/", views.delete_meeting, name="delete_meeting"),
    
    ###################### Certificate Management ############################
    path('staff-certificates/', views.certificate_management, name='certificate_management'),
    path('staff-certificates/<str:cert_type>/<int:cert_id>/approve/', views.approve_certificate,name='approve_certificate'),
    path('staff-certificates/<str:cert_type>/<int:cert_id>/reject/',views.reject_certificate, name='reject_certificate'),
 
    ###################### Manage Schemes ################
    path('staff/schemes/', views.manage_schemes, name='manage_schemes'),
    path('staff/schemes/add/', views.add_scheme, name='add_scheme'),
    path('staff/schemes/edit/<int:scheme_id>/', views.edit_scheme, name='edit_scheme'),
    path('staff/schemes/delete/<int:scheme_id>/', views.delete_scheme, name='delete_scheme'),

    ###################### Helpdesk ############################
    path('staff/helpdesk/', views.manage_helpdesk, name='manage_helpdesk'),
    path('staff/helpdesk/faqs/', views.manage_faqs, name='manage_faqs'),
    path('staff/helpdesk/faqs/add/', views.add_faq, name='add_faq'),
    path('staff/helpdesk/faqs/edit/<int:faq_id>/', views.edit_faq, name='edit_faq'),
    path('staff/helpdesk/faqs/delete/<int:faq_id>/', views.delete_faq, name='delete_faq'),
    path('staff/helpdesk/request/resolve/<int:request_id>/', views.resolve_support_request, name='resolve_support_request'),
    path('staff/helpdesk/request/contact/<int:request_id>/', views.contact_citizen, name='contact_citizen'),


    ##################### Surveys ############################
    path('staff/surveys/', views.manage_surveys, name='manage_surveys'),
    path('staff/surveys/add/', views.add_survey, name='add_survey'),
    path('staff/surveys/edit/<int:survey_id>/', views.edit_survey, name='edit_survey'),
    path('survey/toggle-status/<int:survey_id>/', views.toggle_survey_status, name='toggle_survey_status'),
    path('staff/surveys/delete/<int:survey_id>/', views.delete_survey, name='delete_survey'),
    path('staff/surveys/responses/<int:survey_id>/', views.view_survey_responses, name='view_survey_responses'),
    path('survey/<int:survey_id>/', views.survey_detail, name='survey_detail'),

    path('staff/feedback/', views.manage_feedback, name='manage_feedback'),
    path('staff/feedback/delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),

    ###################### Job Opportunities ############################
    path("staff/job-opportunities/", views.job_opportunities, name="job_opportunities"),
    path("staff/job-opportunities/add/", views.add_job, name="add_job"),
    path("staff/job-opportunities/delete/<int:job_id>/", views.delete_job, name="delete_job"),
    path("staff/job-opportunities/edit/<int:job_id>/", views.edit_job, name="edit_job"),


    #################### Local Tourism ############################
    path("staff/tourism-management/", views.tourism_management, name="tourism_management"),
    path("staff/tourism-management/add/", views.add_tourism, name="add_tourism"),
    path("staff/tourism-management/delete/<int:tourism_id>/", views.delete_tourism, name="delete_tourism"),
    path("staff/tourism-management/edit/<int:tourism_id>/", views.edit_tourism, name="edit_tourism"),


    ##################### Village Dashboard ############################
    path("staff/village-dashboard/", views.manage_village_dashboard, name="manage_village_dashboard"),
    path("staff/village-dashboard/delete/<int:update_id>/", views.delete_village_update, name="delete_village_update"),

    ##################### Panchayat Profiles ############################
    path("staff/panchayat/", views.manage_panchayat, name="manage_panchayat"),
    path("staff/panchayat/add/", views.add_panchayat_member, name="add_panchayat_member"),
    path("staff/panchayat/edit/<int:member_id>/", views.edit_panchayat_member, name="edit_panchayat_member"),
    path("staff/panchayat/delete/<int:member_id>/", views.delete_panchayat_member, name="delete_panchayat_member"),

    ##################### Photo Gallery ############################
    path("staff/gallery/", views.manage_gallery, name="manage_gallery"),
    path("staff/gallery/add/", views.add_gallery_image, name="add_gallery_image"),
    path("staff/gallery/delete/<int:image_id>/", views.delete_gallery_image, name="delete_gallery_image"),

    ####################### Staff Event Management ########################
    path('staff/events/', views.events_management, name='events_management'),
    path('staff/events/add/', views.add_event, name='add_event'),
    path('staff/events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('staff/events/delete/<int:event_id>/', views.delete_event, name='delete_event'),

     ##################### Shramdan Images Management ########################
    path("staff/shramdan/manage/", views.manage_shramdan_events, name="manage_shramdan_events"),
    path("staff/shramdan/delete/<int:event_id>/", views.delete_shramdan_event, name="delete_shramdan_event"),

]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
