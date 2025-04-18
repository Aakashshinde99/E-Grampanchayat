from django.db import models
import os
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

def user_profile_picture_upload_path(instance, filename):
  """
    Stores profile pictures inside: `media/profile_pics/user_{id}/`
    """
  ext = filename.split('.')[-1]
  filename = f"profile_{instance.user.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
  return os.path.join(f"profile_pics/user_{instance.id}/", filename)

class UserProfile(models.Model):
  # ForeignKey to the custom User model
  user = models.ForeignKey(
      settings.AUTH_USER_MODEL, 
      on_delete=models.CASCADE, 
      related_name='profile', 
      blank=True, null=True
  )
  USER_TYPES = [
        ('citizen', _('Citizen')),
        ('staff', _('Staff')),
        ('admin', _('Admin')),
    ]
  user_type = models.CharField(
      max_length=10, choices=USER_TYPES,
      default='citizen')  # ✅ Differentiates user roles
  bio = models.TextField(blank=True, null=True)
  # You can add more fields specific to the user profile here
  birthdate = models.DateField(blank=True, null=True)
  phoneno = models.CharField(max_length=10, unique=True, blank=True, null=True)
  address = models.TextField(blank=True, null=True)
  aadharno = models.CharField(max_length=12,
                              unique=True,
                              blank=True,
                              null=True)
  panno = models.CharField(max_length=10, unique=True, blank=True, null=True)

  # ✅ Profile Picture with Dynamic Upload Path
  profile_picture_base64 = models.TextField(blank=True, null=True)

  def __str__(self):
      return f"Profile of {self.user.username}"


##################### Tax Related Models ########################
class Tax(models.Model):
  tax_name = models.CharField(max_length=255, unique=True)
  description = models.TextField()
  outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2)

  def __str__(self):
    return self.tax_name


class TaxPayment(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Uses new User model
  tax = models.ForeignKey(Tax, on_delete=models.CASCADE)
  payment_id = models.CharField(max_length=255, unique=True)
  amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
  payment_date = models.DateTimeField(auto_now_add=True)
  valid_until = models.DateTimeField(default=now() + timedelta(days=365))

  def __str__(self):
    return f"{self.user.username} - {self.tax.tax_name} - Paid: {self.amount_paid}"
  
  def formatted_date(self):
        return self.payment_date.strftime("%d %B %Y, %H:%M")

  def get_receipt_data(self):
      """ Returns formatted receipt details """
      return {
          "username": self.user.get_full_name() or self.user.username,
          "tax_name": self.tax.tax_name,
          "amount_paid": f"₹{self.amount_paid}",
          "payment_date": self.formatted_date(),
          "payment_id": self.payment_id,
      }


################### Meeting Related Models #######################
from datetime import timedelta, date
class Meeting(models.Model):
  title = models.CharField(max_length=255)
  date = models.DateField()
  time = models.TimeField()
  description = models.TextField()
  location = models.CharField(max_length=255)
  created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
  @property
  def is_new(self):
      recent_days = date.today() - timedelta(days=3)
      return self.date >= recent_days
  def __str__(self):
    return f"{self.title} on {self.date} at {self.time}"


################ Certificates Related Models #######################
# ✅ Utility function to validate past dates
def validate_past_date(value):
  if value > now().date():
    raise ValidationError("Date cannot be in the future.")

# ✅ Function to generate file paths dynamically
def generated_certificate_upload_path(instance, filename):
    return os.path.join(f"certificates/generated/{instance.user.id}/", filename)

# ✅ Generic function to generate dynamic upload paths
def certificate_upload_path(instance, filename, category):
  """Dynamically stores documents inside `media/certificates/{category}/user_{id}/`"""
  ext = filename.split('.')[-1]
  filename = f"{instance.user.id}_{category}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
  return os.path.join(f"certificates/{category}/user_{instance.user.id}/",
                      filename)


# ✅ Separate functions for each certificate type (Django does NOT allow lambda)
def birth_certificate_upload_path(instance, filename):
  return certificate_upload_path(instance, filename, "birth")


def death_certificate_upload_path(instance, filename):
  return certificate_upload_path(instance, filename, "death")


def marriage_certificate_upload_path(instance, filename):
  return certificate_upload_path(instance, filename, "marriage")


def domicile_certificate_upload_path(instance, filename):
  return certificate_upload_path(instance, filename, "domicile")


################# Birth Certificate Model #######################
class BirthCertificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    dob = models.DateField(validators=[validate_past_date])
    parent_name = models.CharField(max_length=255)
    document = models.FileField(upload_to=birth_certificate_upload_path, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    submitted_at = models.DateTimeField(default=timezone.now)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_birth_certificates"
    ) 

    # ✅ NEW: Field to store generated certificate PDF
    generated_certificate = models.FileField(upload_to="generated_certificates/", blank=True, null=True)

    def __str__(self):
        return f"Birth Certificate - {self.full_name}"


################# Death Certificate Model #######################
class DeathCertificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    deceased_name = models.CharField(max_length=255)
    date_of_death = models.DateField(validators=[validate_past_date])
    place_of_death = models.CharField(max_length=255)
    cause_of_death = models.CharField(max_length=255)
    document = models.FileField(upload_to=death_certificate_upload_path)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    submitted_at = models.DateTimeField(default=timezone.now)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_death_certificates"
    ) 

    # Field to store generated certificate PDF
    generated_certificate = models.FileField(upload_to="generated_certificates/", blank=True, null=True)

    def __str__(self):
        return f"Death Certificate - {self.deceased_name}"


################# Marriage Certificate Model #######################
class MarriageCertificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    husband_name = models.CharField(max_length=255)
    wife_name = models.CharField(max_length=255)
    date_of_marriage = models.DateField(validators=[validate_past_date])
    place_of_marriage = models.CharField(max_length=255)
    document = models.FileField(upload_to=marriage_certificate_upload_path)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    submitted_at = models.DateTimeField(default=timezone.now)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_marriage_certificates"
    ) 

    # ✅ NEW: Field to store generated certificate PDF
    generated_certificate = models.FileField(upload_to="generated_certificates/", blank=True, null=True)

    def __str__(self):
        return f"Marriage Certificate - {self.husband_name} & {self.wife_name}"


################# Domicile Certificate Model #######################
class DomicileCertificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    guardian_name = models.CharField(max_length=255)
    address = models.TextField()
    document = models.FileField(upload_to=domicile_certificate_upload_path)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    submitted_at = models.DateTimeField(default=timezone.now)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_domicile_certificates"
    ) 

    # ✅ NEW: Field to store generated certificate PDF
    generated_certificate = models.FileField(upload_to="generated_certificates/", blank=True, null=True)

    def __str__(self):
        return f"Domicile Certificate - {self.full_name}"


######################### Health & Education Scheme Related Models ############################
class Scheme(models.Model):
  CATEGORY_CHOICES = [
      ('health', 'Health'),
      ('education', 'Education'),
  ]

  title = models.CharField(max_length=255)
  eligibility = models.TextField()
  category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
  link = models.CharField(max_length=255,
                          help_text="URL to scheme details",
                          blank=True)

  def __str__(self):
    return self.title


############################## Helpdesk Support Related Models ##############################
from django.db import models
from django.contrib.auth.models import User
class SupportRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="support_requests", null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    message = models.TextField()
    response = models.TextField(blank=True, null=True)  # ✅ Store staff's reply here
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Resolved", "Resolved")], default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"



########################## FAQ Model ##########################
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    views = models.IntegerField(default=0)  # Track most viewed/asked questions

    def __str__(self):
        return self.question

    class Meta:
        ordering = ["-views"]  # Sort by most viewed first

    def increment_views(self):
        self.views += 1
        self.save()


########################## Survey Related Models ############################
from django.db import models
from django.conf import settings

class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    TEXT = "text"
    MULTIPLE_CHOICE = "mcq"
    YES_NO = "yes_no"
    NUMBER = "number"

    QUESTION_TYPES = [
        (TEXT, "Text"),
        (MULTIPLE_CHOICE, "Multiple Choice"),
        (YES_NO, "Yes/No"),
        (NUMBER, "Numeric"),
    ]
    class Meta:
        ordering = ['id']

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default=TEXT)
    choices = models.TextField(blank=True, help_text="Comma-separated choices for MCQ")

    def get_choices(self):
        return self.choices.split(",") if self.question_type == self.MULTIPLE_CHOICE else []

    def __str__(self):
        return self.text

class SurveyResponse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.survey.title}"

class Response(models.Model):
    survey_response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()

    def __str__(self):
        return f"Response to {self.question.text} by {self.survey_response.user.username}"

class Feedback(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL,
                           on_delete=models.CASCADE,
                           null=True,
                           blank=True)  # ✅ Fixed
  message = models.TextField()
  submitted_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Feedback from {self.user.username if self.user else 'Anonymous'}"


############ Event Related Models ################
import base64
from django.db import models
from django.utils.safestring import mark_safe

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    image = models.ImageField(upload_to="event_images/", blank=True, null=True)  # ✅ Keep only the image field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def image_base64(self):
        """Convert image file to Base64 for display."""
        if self.image and self.image.path:
            try:
                with open(self.image.path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode("utf-8")
            except FileNotFoundError:
                return None
        return None


    def image_tag(self):
        """ Returns an HTML image tag for admin preview """
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="150"/>')
        return "(No Image)"
    
    image_tag.short_description = 'Event Image'

############### Job Opportunities (Local Business) ###############
class JobOpportunity(models.Model):
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    contact_email = models.EmailField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} - {self.company_name}"


############### Local Tourism & Assistance ###############
class LocalTourism(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    best_time_to_visit = models.CharField(max_length=255, blank=True, null=True)
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

############### Village Dashboard ###############
class VillageDashboard(models.Model):
    population = models.IntegerField(default=0)
    literacy_rate = models.FloatField(default=0.0)  # In percentage
    ongoing_projects = models.IntegerField(default=0)
    annual_budget = models.CharField(max_length=255, default="Not specified")
    village_location = models.CharField(max_length=255, default="Not specified")  # New field
    employment_rate = models.FloatField(default=0.0)  # New field (Percentage)

    def __str__(self):
        return f"Village Stats - {self.village_location}"

############### Village Updates ###############   
class VillageUpdate(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

############### Panchayat Members ###############
class PanchayatMember(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    image_base64 = models.TextField(blank=True, null=True)  # base64 encoded image

    def __str__(self):
        return f"{self.name} - {self.role}"


############### Gallery ###############
import base64
from django.core.files.base import ContentFile

class GalleryImage(models.Model):
    title = models.CharField(max_length=255, help_text="Title of the event or image")
    image = models.ImageField(upload_to="gallery/", help_text="Upload an image for the gallery")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def base64(self):
        """Return base64 string of the image for inline rendering."""
        if self.image:
            try:
                with self.image.open("rb") as img_file:
                    encoded = base64.b64encode(img_file.read()).decode("utf-8")
                    # Handle image type detection dynamically
                    extension = self.image.name.split('.')[-1].lower()
                    return f"data:image/{extension};base64,{encoded}"
            except Exception as e:
                return ""
        return ""


############### Notifications ###############  
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("success", "Success"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default="info")
    is_read = models.BooleanField(default=False)  # Used to track if notification is read
    created_at = models.DateTimeField(default=now)
    related_object_id = models.IntegerField(blank=True, null=True)  # ID of related object (optional)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:30]}"

########### Shramdan and Abhiyaans Events ###############
class ShramdanEvent(models.Model):
    name = models.CharField(max_length=255)
    image_base64 = models.TextField(help_text="Base64-encoded image")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
