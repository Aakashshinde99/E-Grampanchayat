from django.contrib import admin
from .models import (UserProfile, 
                     Meeting, 
                     BirthCertificate, 
                     DeathCertificate, 
                     MarriageCertificate, 
                     DomicileCertificate, 
                     Scheme, 
                     SupportRequest, 
                     Survey, 
                     SurveyResponse, 
                     Feedback, 
                     Event, 
                     Tax, 
                     TaxPayment, 
                     Notification, 
                     JobOpportunity,
                     LocalTourism,
                     VillageDashboard,
                     FAQ,
)

# Register models
admin.site.register(UserProfile)
admin.site.register(Meeting)
admin.site.register(BirthCertificate)
admin.site.register(DeathCertificate)
admin.site.register(MarriageCertificate)
admin.site.register(DomicileCertificate)
admin.site.register(Scheme)
admin.site.register(SupportRequest)
admin.site.register(FAQ)
admin.site.register(Survey)
admin.site.register(SurveyResponse)
admin.site.register(Feedback)
admin.site.register(Event)
admin.site.register(Tax)
admin.site.register(TaxPayment)
admin.site.register(Notification)
admin.site.register(JobOpportunity)
admin.site.register(LocalTourism)
admin.site.register(VillageDashboard)

