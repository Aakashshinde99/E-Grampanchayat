from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Notification
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.utils.translation import activate
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import TaxPayment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import VillageDashboard
from gramapp.models import VillageDashboard, VillageUpdate
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Survey, SurveyResponse, Feedback
from django.utils.timezone import now
import base64

import io
from .models import (
    UserProfile, 
    BirthCertificate, 
    DeathCertificate, 
    MarriageCertificate, 
    DomicileCertificate, 
    Tax, 
    TaxPayment, 
    SupportRequest, 
    Survey, 
    SurveyResponse, 
    Feedback, 
    Scheme, 
    Event,
    Meeting,
    JobOpportunity,
    LocalTourism,
    Notification,
    Meeting,
    PanchayatMember,
    FAQ,
    Notification,
)
import os

############### Language Switcher ###############
from django.shortcuts import redirect
from django.utils.translation import activate, get_language
from django.conf import settings

def switch_language(request, lang_code):
    """ Switch language, activate it, and reload the page """
    
    if lang_code not in dict(settings.LANGUAGES):
        return redirect(request.GET.get('next', '/'))  # Invalid language, do nothing

    # ✅ Store language in session (for logged-in users)
    request.session['django_language'] = lang_code

    # ✅ Store language in cookie (for guests)
    response = redirect(request.GET.get('next', '/'))
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code, max_age=365*24*60*60)

    # ✅ Force activate the language immediately
    activate(lang_code)

    print(f"🔹 Language Switched to {lang_code}, Active Language: {get_language()}")  # Debugging

    return response


from django.http import JsonResponse
from django.utils.translation import get_language

def debug_language(request):
    """ View to check if language is stored in session and cookies """
    return JsonResponse({
        "session_language": request.session.get('django_language', "Not Set"),
        "cookie_language": request.COOKIES.get('django_language', "Not Set"),
        "active_language": get_language()
    })


######################################### User related functions ##########################################

############# Home Page ###############
def home_view(request):
    """
    Render the home page for the Grampanchayat portal.
    """
    return render(request, 'home.html', {'hide_profile_menu': True})

############ user login #############
from django.contrib.auth.hashers import check_password
# from .models import User


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)  # ✅ Authenticate user

        if user:
            try:
                # ✅ Fetch user profile to check user_type
                user_profile = UserProfile.objects.get(user=user)

                if user_profile.user_type == "citizen":  # ✅ Allow only citizens
                    login(request, user)  
                    return redirect("dashboard_view")  # Citizen Dashboard
                
                elif user_profile.user_type == "staff":
                    messages.error(request, "Staff members must log in via the staff portal.")
                    return redirect("staff_login")  # Redirect staff to staff login
                
                else:
                    messages.error(request, "Invalid user type. Contact admin.")
                    return redirect("login_view")  # Block any unexpected user types

            except UserProfile.DoesNotExist:
                messages.error(request, "User profile not found! Contact admin.")
                return redirect("login_view")

        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login_view")

    return render(request, "user/user_login.html")


############ user registration #############
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
# from .models import User
import re

def register_view(request):
    if request.method == 'POST':
        # ✅ Capture new fields
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        phoneno = request.POST['phoneno']
        address = request.POST['address']
        aadharno = request.POST['aadharno']
        panno = request.POST['panno']
        profile_picture = request.FILES.get('profile_picture')  # Get uploaded image

        # ✅ Validate password match
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register_view')

        # ✅ Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messages.error(request, "Invalid email format!")
            return redirect('register_view')

        # ✅ Validate phone number
        if not phoneno.isdigit() or len(phoneno) != 10:
            messages.error(request, "Phone number must be exactly 10 digits!")
            return redirect('register_view')

        # ✅ Validate Aadhar number
        if not aadharno.isdigit() or len(aadharno) != 12:
            messages.error(request, "Aadhar number must be exactly 12 digits!")
            return redirect('register_view')

        # ✅ Validate PAN format
        pan_regex = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
        if not re.match(pan_regex, panno):
            messages.error(request, "Invalid PAN number format!")
            return redirect('register_view')

        # ✅ Check for duplicates
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('register_view')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('register_view')

        if UserProfile.objects.filter(phoneno=phoneno).exists():
            messages.error(request, "Phone number already in use!")
            return redirect('register_view')

        if UserProfile.objects.filter(aadharno=aadharno).exists():
            messages.error(request, "Aadhar number already registered!")
            return redirect('register_view')

        if UserProfile.objects.filter(panno=panno).exists():
            messages.error(request, "PAN number already registered!")
            return redirect('register_view')

        # ✅ Create User
        user = User.objects.create(
            first_name=first_name,  # ✅ Store first name
            last_name=last_name,  # ✅ Store last name
            username=username,
            email=email,
            password=make_password(password1)  # ✅ Hash password
        )

        # 🔹 Convert Image to Base64
        profile_picture_base64 = ""
        if profile_picture:
            profile_picture_content = profile_picture.read()  # Read file content
            profile_picture_base64 = base64.b64encode(profile_picture_content).decode('utf-8')

        # ✅ Create UserProfile
        UserProfile.objects.create(
            user=user,
            phoneno=phoneno,
            address=address,
            aadharno=aadharno,
            panno=panno,
            profile_picture_base64=profile_picture_base64,  # Store Base64 string
            user_type="citizen"  # ✅ Default user type is 'citizen'
        )

        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login_view')

    return render(request, 'user/user_register.html', {'hide_profile_menu': True})


############ user dashboard #############
from django.utils.translation import gettext_lazy as _  # ✅ Import translation function
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required(login_url='login_view')  # ✅ Redirects if not logged in
def dashboard_view(request):
    """User dashboard displaying all available features."""
    
    # ✅ Fetch user profile safely
    user_profile = UserProfile.objects.filter(user=request.user).first()
    
    if not user_profile:  # ✅ Handle case where profile is missing
        return redirect('home_view')

    if user_profile.user_type != "citizen":
        return redirect('home_view')

    context = {
        "user_details": request.user,  # ✅ Use request.user instead of session
        "features": [
            {"title": _("Water and Property Tax"), "description": _("Manage and pay your taxes efficiently."), "button_text": _("View Details"), "url_name": "tax"},
            {"title": _("Shramdan & Abhiyaans"), "description": _("Participate in community initiatives."), "button_text": _("Explore Events"), "url_name": "shramdan_page"},
            {"title": _("Gramsabha Meetings"), "description": _("Stay updated on upcoming discussions."), "button_text": _("See Schedule"), "url_name": "sabha_meetings_page"},
            {"title": _("Certificates"), "description": _("Apply for birth, death or marriage certificates."), "button_text": _("Apply Now"), "url_name": "certificates_page"},
            {"title": _("Health & Education Schemes"), "description": _("Explore available schemes and benefits."), "button_text": _("Learn More"), "url_name": "health_education_page"},
            {"title": _("Helpdesk Support"), "description": _("Get assistance with your queries."), "button_text": _("Contact Us"), "url_name": "helpdesk_page"},
            {"title": _("Surveys"), "description": _("Contribute your opinions and feedback."), "button_text": _("Participate"), "url_name": "surveys"},
            {"title": _("Event Announcements"), "description": _("Check out the latest events in the village."), "button_text": _("View Events"), "url_name": "events"},
            {"title": _("Photo Gallery"), "description": _("Relive memories from past events."), "button_text": _("Browse Photos"), "url_name": "user_gallery"},
            {"title": _("Village Dashboard"), "description": _("Access village statistics and updates."), "button_text": _("View Dashboard"), "url_name": "village_dashboard"},
            {"title": _("Panchayat Profiles"), "description": _("Learn about Panchayat members and their roles."), "button_text": _("Meet the Team"), "url_name": "panchayat_profile"},
            {"title": _("Job Opportunities"), "description": _("Find job openings in your village."), "button_text": _("View Jobs"), "url_name": "user_job_opportunities"},
            {"title": _("Local Tourism & Assistance"), "description": _("Explore local tourist spots & help services."), "button_text": _("View Locations"), "url_name": "user_tourism"},
        ]
    }

    return render(request, 'user/user_dashboard.html', context)

################ User Profile ##################
@login_required(login_url='login_view')
def user_profile(request):
    try:
        user_profile = request.user.profile.get()  # ✅ Fetch UserProfile instance correctly
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile does not exist.")
        return redirect("dashboard_view")  # Redirect if no profile exists

    if user_profile.user_type != "citizen":  # ✅ Restrict to citizens only
        return redirect("home_view")  # Redirect staff to their dashboard

    applied_services = {
        "Birth Certificates": BirthCertificate.objects.filter(user=request.user),
        "Death Certificates": DeathCertificate.objects.filter(user=request.user),
        "Marriage Certificates": MarriageCertificate.objects.filter(user=request.user),
        "Domicile Certificates": DomicileCertificate.objects.filter(user=request.user),
    }

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    context = {
        "user_details": request.user,  # ✅ Fetch user (for name & email)
        "user_profile": user_profile,  # ✅ Fetch UserProfile correctly
        "applied_services": applied_services
    }

    return render(request, 'user/user_profile.html', context)



########### User Logout Button ############
def logout_view(request):
    logout(request)  # ✅ Logs out the user
    messages.success(request, "Logged out successfully.")
    return redirect('home_view')


####################################### Water and Property Tax  ######################################
@login_required(login_url='login_view')
def tax_page(request):
    taxes = Tax.objects.all()
    tax_payments = TaxPayment.objects.filter(user=request.user).order_by("-payment_date")

    # Check if user has already paid for each tax type
    for tax in taxes:
        last_payment = TaxPayment.objects.filter(user=request.user, tax=tax).order_by('-payment_date').first()
        if last_payment and last_payment.valid_until > now():
            tax.outstanding_amount = 0  # Set outstanding amount to 0 if paid for 1 year

    return render(request, "user/Water_Property_Tax/tax.html", {"taxes": taxes, "tax_payments": tax_payments})

@login_required(login_url='login_view')
def payment_success(request):
    """API endpoint to update the database when a payment is successful."""
    if request.method == "POST":
        tax_id = request.POST.get("tax_id")
        payment_id = request.POST.get("payment_id")
        amount_paid = request.POST.get("amount_paid")

        tax = get_object_or_404(Tax, id=tax_id)

        # Create the tax payment record
        tax_payment = TaxPayment.objects.create(
            user=request.user,
            tax=tax,
            payment_id=payment_id,
            amount_paid=amount_paid
        )

        # Get receipt details
        receipt_data = tax_payment.get_receipt_data()

        return JsonResponse({"status": "success", "message": "Payment recorded successfully!", "receipt": receipt_data})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


######################### Generate Tax Receipt #######################
@login_required(login_url='login_view')
def generate_tax_receipt(request, payment_id):
    """ Generate a PDF receipt for the given payment. """
    payment = get_object_or_404(TaxPayment, payment_id=payment_id)

    # Create PDF file in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle(f"Tax_Receipt_{payment.payment_id}.pdf")

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 750, "Panchayat Tax Payment Receipt")

    # Details
    p.setFont("Helvetica", 12)
    p.drawString(100, 700, f"Citizen: {payment.user.get_full_name()}")
    p.drawString(100, 680, f"Payment ID: {payment.payment_id}")
    p.drawString(100, 660, f"Tax Type: {payment.tax.tax_name}")
    p.drawString(100, 640, f"Amount Paid: {payment.amount_paid}")
    p.drawString(100, 620, f"Payment Date: {payment.payment_date.strftime('%d %b %Y, %H:%M')}")

    # Footer
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, 580, "Thank you for your payment! Keep this receipt for your records.")

    # Save the PDF
    p.showPage()
    p.save()

    # Serve the PDF
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Tax_Receipt_{payment.payment_id}.pdf"'
    return response


##################### Shramdan & Abhiyaans #################
@login_required(login_url='login_view')
def shramdan_page(request):
    # Sample photos and events for the horizontal scroll
    events = [
        {"name": "Event 1", "image_url": "https://via.placeholder.com/300"},
        {"name": "Event 2", "image_url": "https://via.placeholder.com/300"},
        {"name": "Event 3", "image_url": "https://via.placeholder.com/300"},
        {"name": "Event 4", "image_url": "https://via.placeholder.com/300"},
        {"name": "Event 5", "image_url": "https://via.placeholder.com/300"},
    ]
    # Pass event data to the template
    context = {
        "events": events
    }
    return render(request, "user/Shramdan_Abhiyaan/shramdan.html", context)

################## Sabha Meetings #############
@login_required(login_url='login_view')
def sabha_meetings_page(request):
    meetings = Meeting.objects.all()
    return render(request, "user/Gramsabha_Meetings/sabhameet.html", {"meetings": meetings})

############################################ Certificates Page ###########################################
@login_required(login_url='login_view')
def certificates_page(request):
    """ Show available certificates and user's applied services """

    # ✅ Fetch applied certificates
    applied_services = {
        "Birth Certificates": BirthCertificate.objects.filter(user=request.user),
        "Death Certificates": DeathCertificate.objects.filter(user=request.user),
        "Marriage Certificates": MarriageCertificate.objects.filter(user=request.user),
        "Domicile Certificates": DomicileCertificate.objects.filter(user=request.user),
    }

    context = {
        "applied_services": applied_services,  # ✅ Pass applied certificates
    }
    return render(request, "user/Certificates/certificates.html", context)


@csrf_exempt
@login_required(login_url='login_view')
def apply_birth_certificate(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        dob = request.POST.get('dob')
        parent_name = request.POST.get('parent_name')

        if 'document' not in request.FILES:
            messages.error(request, _("Please upload a document."))
            return redirect('apply_birth_certificate')
        document = request.FILES.get('document')

        if not document.name.endswith('.pdf'):
            messages.error(request, _("Only PDF files are allowed!"))
            return JsonResponse({"status": "error", "message": _("Only PDF files are allowed!")}, status=400)

        birth_cert = BirthCertificate.objects.create(
            user=request.user,
            full_name=full_name,
            dob=dob,
            parent_name=parent_name,
            document=document
        )

        messages.success(request, _("Application submitted successfully!"))
        return JsonResponse({"status": "success", "message": _("Application submitted successfully!")}, status=200)

    return render(request, 'user/Certificates/birth_certificate.html')

@csrf_exempt
@login_required(login_url='login_view')
def apply_death_certificate(request):
    if request.method == 'POST':
        deceased_name = request.POST.get('deceased_name')
        date_of_death = request.POST.get('date_of_death')
        place_of_death = request.POST.get('place_of_death')
        cause_of_death = request.POST.get('cause_of_death')
        
        # ✅ Ensure document input name matches the template
        document = request.FILES.get('document')  

        # ✅ Check for missing fields
        if not all([deceased_name, date_of_death, place_of_death, cause_of_death, document]):
            messages.error(request, _("All fields are required."))
            return redirect('apply_death_certificate')

        # ✅ Save to database
        DeathCertificate.objects.create(
            user=request.user,
            deceased_name=deceased_name,
            date_of_death=date_of_death,
            place_of_death=place_of_death,
            cause_of_death=cause_of_death,
            document=document
        )

        messages.success(request, _("Death Certificate Application Submitted Successfully."))
        return redirect('certificates_page')

    return render(request, 'user/Certificates/death_certificate.html')

@csrf_exempt
@login_required(login_url='login_view')
def apply_marriage_certificate(request):
    if request.method == 'POST':
        husband_name = request.POST.get('husband_name')
        wife_name = request.POST.get('wife_name')
        date_of_marriage = request.POST.get('date_of_marriage')
        place_of_marriage = request.POST.get('place_of_marriage')
        
        # ✅ Ensure document input name matches the template
        document = request.FILES.get('document')  

        # ✅ Check if all fields are filled
        if not all([husband_name, wife_name, date_of_marriage, place_of_marriage, document]):
            messages.error(request, _("All fields are required."))
            return redirect('apply_marriage_certificate')

        # ✅ Validate File Type (Only PDF)
        if not document.name.endswith('.pdf'):
            messages.error(request, _("Only PDF files are allowed!"))
            return redirect('apply_marriage_certificate')

        # ✅ Save to database
        MarriageCertificate.objects.create(
            user=request.user,
            husband_name=husband_name,
            wife_name=wife_name,
            date_of_marriage=date_of_marriage,
            place_of_marriage=place_of_marriage,
            document=document
        )

        messages.success(request, _("Your marriage certificate application has been submitted."))
        return redirect('certificates_page')

    return render(request, 'user/Certificates/marriage_certificate.html')

@csrf_exempt
@login_required(login_url='login_view')
def apply_domicile_certificate(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        guardian_name = request.POST.get('guardian_name')
        address = request.POST.get('address')

        # ✅ Ensure document input name matches the template
        document = request.FILES.get('document')  

        # ✅ Check if all fields are filled
        if not all([full_name, guardian_name, address, document]):
            messages.error(request, _("All fields are required."))
            return redirect('apply_domicile_certificate')

        # ✅ Validate File Type (Only PDF)
        if not document.name.endswith('.pdf'):
            messages.error(request, _("Only PDF files are allowed!"))
            return redirect('apply_domicile_certificate')

        # ✅ Save to database
        DomicileCertificate.objects.create(
            user=request.user,
            full_name=full_name,
            guardian_name=guardian_name,
            address=address,
            document=document
        )

        messages.success(request, _("Your domicile certificate application has been submitted."))
        return redirect('certificates_page')

    return render(request, 'user/Certificates/domicile_certificate.html')

############### Health and Educational Services #############
@login_required(login_url='login_view')
def health_education_page(request):
    health_schemes = Scheme.objects.filter(category="health")
    education_schemes = Scheme.objects.filter(category="education")

    context = {
        "health_schemes": health_schemes,
        "education_schemes": education_schemes,
    }
    return render(request, "user/Health_Education/healthedu.html", context)


################### Help Desk Support ####################
def helpdesk_page(request):
    """ User can view Helpdesk support and FAQs """
    faqs = FAQ.objects.all().order_by("-id")  # ✅ Fetch all FAQs from the database

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        SupportRequest.objects.create(
            name=name, email=email, phone=phone, message=message
        )
        messages.success(request, "Your request has been submitted successfully!")
        return redirect("helpdesk_page")

    return render(request, "user/Helpdesk/helpdesk.html", {"faqs": faqs})  # ✅ Pass FAQs to template




################ Surveys #################
@login_required(login_url='login_view')
def surveys(request):
    return render(request, 'user/Surveys/surveys.html')

@login_required(login_url='login_view')
def surveys_ongoing(request):
    surveys = Survey.objects.filter(is_active=True)
    # Get a list of completed survey IDs for the logged-in user
    completed_surveys = SurveyResponse.objects.filter(user=request.user).values_list('survey_id', flat=True)

    return render(request, 'user/Surveys/surveys_ongoing.html', {
        'surveys': surveys,
        'completed_surveys': list(completed_surveys),
    })

from .models import Feedback
@login_required(login_url='login_view')
def submit_feedback(request):
    """ Allows users to submit feedback """
    if request.method == "POST":
        message = request.POST.get('feedback')
        
        if message:
            # ✅ Ensure feedback is stored properly
            Feedback.objects.create(user=request.user, message=message)
            messages.success(request, "📨 Feedback submitted successfully!")
            return redirect('surveys')  
    
    return render(request, 'user/Surveys/submit_feedback.html')

@login_required(login_url='login_view')
def survey_results(request):
    surveys = Survey.objects.filter(is_active=False)  # Fetch only completed surveys

    return render(request, 'user/Surveys/survey_results.html', {
        'surveys': surveys,
    })



################  Events Announcements  ############
@login_required(login_url='login_view')
def events(request):
    """ Fetch all events from the database and pass them to the template. """
    all_events = Event.objects.all().order_by('-date')  # ✅ Fetch events sorted by latest date
    return render(request, 'user/Events/events.html', {"events": all_events})

################ Photo Gallery Page ################
@login_required(login_url='login_view')
def user_gallery(request):
    return render(request, 'user/Photo_Gallery/gallery.html')

################ Village Dashboard ################
@login_required(login_url='login_view')
def village_dashboard(request):
    """ User view for Village Dashboard showing key village statistics """
    village_stats = VillageDashboard.objects.first()  # Get the latest village stats
    updates = VillageUpdate.objects.all().order_by("-created_at")[:5]  # Get recent updates

    context = {
        "village_stats": village_stats,  # ✅ Pass statistics
        "updates": updates,  # ✅ Pass recent updates
    }
    
    return render(request, "user/Village_Dashboard/village_dashboard.html", context)


################ Panchayat Profiles ###############
@login_required(login_url='login_view')
def panchayat_profile(request):
    """ Fetches Panchayat members dynamically from the database """
    members = PanchayatMember.objects.all()
    return render(request, "user/Panchayat_Profiles/panchayat_profile.html", {"members": members})



############### User View: Job Opportunities #################
@login_required(login_url='login_view')
def user_job_opportunities(request):
    """ Citizens can view job opportunities """
    jobs = JobOpportunity.objects.all()

    # Convert salary to LPA format before passing to the template
    for job in jobs:
        if job.salary:
            job.salary_lpa = f"{job.salary / 100000:.1f} LPA"  # Convert to LPA (1 decimal place)
        else:
            job.salary_lpa = "Not specified"

    return render(request, "user/Jobs/job_opportunities.html", {"jobs": jobs})


############### User View: Local Tourism #################
@login_required(login_url='login_view')
def user_tourism(request):
    """ Citizens can view tourism places """
    places = LocalTourism.objects.all()
    return render(request, "user/Tourism/tourism.html", {"places": places})

############### User View: Notifications #################
@login_required(login_url='login_view')
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by("-created_at")[:5]
    notification_list = [{"message": n.message, "created_at": n.created_at.strftime("%d %b %Y, %H:%M")} for n in notifications]
    return JsonResponse({"notifications": notification_list, "unread_count": notifications.count()})


#################################### Staff related views #####################################

################## staff login view ##################
def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            try:
                # ✅ Fetch the user profile linked to the authenticated user
                user_profile = UserProfile.objects.get(user=user)

                if user_profile.user_type == 'staff':  # ✅ Check if user is staff
                    login(request, user)
                    return redirect('staff_dashboard')  # Redirect to staff dashboard
                else:
                    return redirect('dashboard_view')  # Redirect citizens to their dashboard

            except UserProfile.DoesNotExist:
                messages.error(request, "User profile not found!")

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'staff/staff_login.html', {'hide_profile_menu': True})


################## staff logout view ##################
@login_required(login_url='staff_login')
def staff_logout(request):
    logout(request)  # ✅ Uses Django's logout function
    messages.success(request, "Logged out successfully.")
    return redirect('staff_login')

#################### staff profile view ##################
@login_required(login_url='staff_login')
def staff_profile(request):
    """Staff profile view showing assigned certificates and details."""
    try:
        staff_profile = UserProfile.objects.get(user=request.user)

        if staff_profile.user_type != "staff":
            messages.error(request, "Unauthorized access!")
            return redirect("home_view")

        # ✅ Fetch Assigned Certificates for Approval
        assigned_certificates = {
            "Birth Certificates": BirthCertificate.objects.filter(approved_by=request.user),
            "Death Certificates": DeathCertificate.objects.filter(approved_by=request.user),
            "Marriage Certificates": MarriageCertificate.objects.filter(approved_by=request.user),
            "Domicile Certificates": DomicileCertificate.objects.filter(approved_by=request.user),
        }

        context = {
            "staff_profile": staff_profile,
            "staff_user": request.user,
            "assigned_certificates": assigned_certificates,
        }

        return render(request, "staff/staff_profile.html", context)

    except UserProfile.DoesNotExist:
        messages.error(request, "Profile not found! Please contact the administrator.")
        return redirect("home_view")

################### staff dashboard view #########################
@login_required(login_url='staff_login')
def staff_dashboard(request):
    """ Staff dashboard displaying all management options. """
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        print(f"User Profile: {user_profile.user_type}")  # Debugging

        if user_profile.user_type != "staff":
            print("User Profile does not exist")  # Debugging
            return redirect("dashboard_view")


        tax_payments = TaxPayment.objects.select_related("user", "tax").order_by("-payment_date")
        total_jobs = JobOpportunity.objects.count()  # Count job postings
        total_tourism = LocalTourism.objects.count()  # Count tourism places
        village_stats = VillageDashboard.objects.first()  # Get first entry if exists
        village_location = village_stats.village_location if village_stats else "Not Specified"
        employment_rate = village_stats.employment_rate if village_stats else 0.0
        total_meetings = Meeting.objects.count()
        total_images = GalleryImage.objects.count() 
        total_panchayat_members = PanchayatMember.objects.count()  # ✅ Count Panchayat members
        total_surveys = Survey.objects.count()  # Count total surveys
        active_surveys = Survey.objects.filter(is_active=True).count()  # Count active surveys

        context = {
            "user_profile": user_profile,  # ✅ Pass it explicitly
            "pending_certificates": BirthCertificate.objects.filter(status="Pending").count() +
                                    DeathCertificate.objects.filter(status="Pending").count() +
                                    MarriageCertificate.objects.filter(status="Pending").count() +
                                    DomicileCertificate.objects.filter(status="Pending").count(),
            "pending_complaints": SupportRequest.objects.filter(status="Pending").count(),
            "tax_payments": tax_payments,
            "total_jobs": total_jobs,
            "total_tourism": total_tourism,
            "village_location": village_location,  # ✅ Added
            "employment_rate": employment_rate,  # ✅ Added
            "total_panchayat_members": total_panchayat_members,  # ✅ Pass to template
            "total_meetings": total_meetings,
            "total_images": total_images,
            "total_surveys": total_surveys,
            "active_surveys": active_surveys,
        }

        return render(request, "staff/staff_dashboard.html", context)

    except UserProfile.DoesNotExist:
        return redirect("staff_login")

################### Staff Tax Management View #########################
@login_required(login_url='staff_login')
def tax_management(request):
    # ✅ Get the UserProfile instance correctly
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.user_type != "staff":  # ✅ Ensure only staff can access
        return redirect("dashboard_view")

    taxes = Tax.objects.all()
    tax_payments = TaxPayment.objects.all().order_by("-payment_date")  # Show recent payments first

    context = {
        "taxes": taxes,
        "tax_payments": tax_payments
    }
    return render(request, "staff/tax/tax_management.html", context)

############# Add Tax View #######################
@login_required(login_url='staff_login')
def add_tax(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    if request.method == "POST":
        tax_name = request.POST.get("tax_name")
        description = request.POST.get("description", "")
        outstanding_amount = request.POST.get("outstanding_amount")

        if not tax_name or not outstanding_amount:
            messages.error(request, "All fields are required!")
            return redirect("add_tax")

        # Ensure tax name is unique
        if Tax.objects.filter(tax_name=tax_name).exists():
            messages.error(request, "A tax with this name already exists.")
            return redirect("add_tax")

        # Create the new tax
        Tax.objects.create(
            tax_name=tax_name,
            description=description,
            outstanding_amount=outstanding_amount
        )
        messages.success(request, f"New tax '{tax_name}' added successfully!")
        return redirect("tax_management")

    return render(request, "staff/tax/add_tax.html")

################ Edit Tax View #######################  
@login_required(login_url='staff_login')
def edit_tax(request, tax_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    tax = get_object_or_404(Tax, id=tax_id)

    if request.method == "POST":
        new_amount = request.POST.get("outstanding_amount")

        # Update the tax amount
        tax.outstanding_amount = new_amount
        tax.save()

        messages.success(request, f"Updated {tax.tax_name} tax amount to ₹{new_amount}.")
        return redirect("tax_management")

    return render(request, "staff/tax/edit_tax.html", {"tax": tax})

############## Manage Meetings View #######################
@login_required(login_url='staff_login')
def manage_meetings(request):
    """ Staff can view and manage meetings """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    meetings = Meeting.objects.all()
    return render(request, "staff/meeting/manage_meetings.html", {"meetings": meetings})


@login_required(login_url='staff_login')
def add_meeting(request):
    """ Staff can add new meetings """
    if request.method == "POST":
        title = request.POST.get("title")
        date = request.POST.get("date")
        time = request.POST.get("time")
        description = request.POST.get("description")
        location = request.POST.get("location")

        Meeting.objects.create(
            title=title,
            date=date,
            time=time,
            description=description,
            location=location,
            created_by=request.user,
        )
        messages.success(request, "📅 Meeting added successfully!")
        return redirect("manage_meetings")

    return render(request, "staff/meeting/add_meeting.html")


@login_required(login_url='staff_login')
def delete_meeting(request, meeting_id):
    """ Staff can delete a meeting """
    meeting = get_object_or_404(Meeting, id=meeting_id)

    if request.method == "POST":
        meeting.delete()
        messages.success(request, "🚫 Meeting deleted successfully!")
        return redirect("manage_meetings")

    return render(request, "staff/meeting/delete_meeting.html", {"meeting": meeting})


################### Certificate Management View #######################
from django.utils.translation import gettext as _

CERTIFICATE_TYPE_TRANSLATIONS = {
    "birth": _("Birth"),
    "death": _("Death"),
    "marriage": _("Marriage"),
    "domicile": _("Domicile"),
}

@login_required(login_url='staff_login')
def certificate_management(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.user_type != "staff":
            return redirect("dashboard_view")

        certificates = {
            "birth": BirthCertificate.objects.filter(status="Pending"),
            "death": DeathCertificate.objects.filter(status="Pending"),
            "marriage": MarriageCertificate.objects.filter(status="Pending"),
            "domicile": DomicileCertificate.objects.filter(status="Pending"),
        }

        # Translate certificate type names
        translated_certificates = {
            CERTIFICATE_TYPE_TRANSLATIONS[key]: value for key, value in certificates.items()
        }

        return render(
            request, 
            "staff/certificate/certificate_management.html",
            {"certificates": translated_certificates}
        )
    except UserProfile.DoesNotExist:
        return redirect("dashboard_view")

############# Generate Certificate View #######################
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from django.core.files.base import ContentFile
import io
import qrcode
from django.conf import settings
import os

def generate_certificate_pdf(certificate):
    """
    Generates a professional-looking PDF certificate with styling, logo, and a QR code.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ✅ Panchayat Logo
    logo_path = os.path.join(settings.MEDIA_ROOT, 'panchayat_logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 50, height - 150, 100, 100)

    # ✅ Certificate Title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(black)
    c.drawCentredString(width / 2, height - 100, "Government of India")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 130, "Gram Panchayat Certificate")

    # ✅ Certificate Details (Updated)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 200, f"Certificate Type: {certificate.__class__.__name__}")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 230, f"Certificate ID: {certificate.id}")
    c.drawString(100, height - 260, f"Name: {certificate.user.first_name} {certificate.user.last_name}")

    # ✅ Corrected Status Display
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(blue if certificate.status == "Approved" else red)
    c.drawString(100, height - 290, f"Status: {certificate.status}")

    # ✅ Issue Date
    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    c.drawString(100, height - 320, f"Issue Date: {certificate.submitted_at.strftime('%d-%m-%Y')}")

    # ✅ QR Code (For Verification)
    qr = qrcode.make(f"Certificate ID: {certificate.id}\nIssued To: {certificate.user.first_name} {certificate.user.last_name}\nStatus: {certificate.status}")
    qr_path = os.path.join(settings.MEDIA_ROOT, f"qr_{certificate.id}.png")
    qr.save(qr_path)
    c.drawImage(qr_path, width - 150, height - 300, 100, 100)

    # ✅ Signature Section
    c.setFont("Helvetica", 12)
    c.drawString(100, 150, "_________________________")
    c.drawString(100, 130, "Authorized Signatory")
    c.drawString(100, 110, "Gram Panchayat Office")

    c.drawString(width - 250, 150, "_________________________")
    c.drawString(width - 250, 130, "Government Seal")

    # ✅ Save the PDF
    c.save()
    pdf_file = ContentFile(buffer.getvalue(), f"certificate_{certificate.id}.pdf")
    return pdf_file


############# Approve Certificate View #######################
from django.core.files.base import ContentFile

@login_required(login_url='staff_login')
def approve_certificate(request, cert_type, cert_id):
    user_profile = request.user.profile.first()

    if not user_profile or user_profile.user_type != "staff":
        messages.error(request, "Unauthorized access!")
        return redirect("dashboard_view")

    model_map = {
        "birth": BirthCertificate,
        "death": DeathCertificate,
        "marriage": MarriageCertificate,
        "domicile": DomicileCertificate,
    }

    if cert_type not in model_map:
        messages.error(request, "Invalid certificate type.")
        return redirect("certificate_management")

    model = model_map[cert_type]
    certificate = get_object_or_404(model, id=cert_id)

    # ✅ Update status before generating the PDF
    certificate.status = "Approved"
    certificate.approved_by = request.user
    certificate.save()

    # ✅ Generate and attach the updated PDF
    pdf_file = generate_certificate_pdf(certificate)  # Now includes "Approved"
    certificate.generated_certificate.save(pdf_file.name, pdf_file, save=True)

    # ✅ Send a notification to the citizen
    Notification.objects.create(
        user=certificate.user,
        message=f"Your {cert_type.capitalize()} Certificate has been approved! 🎉",
        notification_type="success",
        related_object_id=certificate.id,
    )

    messages.success(request, f"{cert_type.capitalize()} Certificate Approved!")
    return redirect("certificate_management")

############# Reject Certificate View #######################
@login_required(login_url='staff_login')
def reject_certificate(request, cert_type, cert_id):
    user_profile = request.user.profile.first()
    
    if not user_profile or user_profile.user_type != "staff":
        messages.error(request, "Unauthorized access!")
        return redirect("dashboard_view")

    model_map = {
        "birth": BirthCertificate,
        "death": DeathCertificate,
        "marriage": MarriageCertificate,
        "domicile": DomicileCertificate,
    }

    if cert_type not in model_map:
        messages.error(request, "Invalid certificate type.")
        return redirect("certificate_management")

    model = model_map[cert_type]
    certificate = get_object_or_404(model, id=cert_id)

    certificate.status = "Rejected"
    certificate.save()

    # ✅ Send notification on rejection
    Notification.objects.create(
        user=certificate.user,
        message=f"Your {cert_type.capitalize()} Certificate has been rejected."
    )
    
    messages.warning(request, f"{cert_type.capitalize()} Certificate Rejected.")
    return redirect("certificate_management")

####################### Manage Schemes from Staff ########################
@login_required(login_url='staff_login')
def manage_schemes(request):
    """ Staff can view and manage all schemes """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    health_schemes = Scheme.objects.filter(category="health")
    education_schemes = Scheme.objects.filter(category="education")

    return render(request, "staff/schems/manage_schemes.html", {
        "health_schemes": health_schemes,
        "education_schemes": education_schemes
    })


@login_required(login_url='staff_login')
def add_scheme(request):
    """ Staff can add new schemes """
    if request.method == "POST":
        title = request.POST.get("title")
        eligibility = request.POST.get("eligibility")
        category = request.POST.get("category")
        link = request.POST.get("link")

        if title and category:
            Scheme.objects.create(title=title, eligibility=eligibility, category=category, link=link)
            messages.success(request, "✅ Scheme added successfully!")
            return redirect("manage_schemes")

    return render(request, "staff/schems/add_scheme.html")


@login_required(login_url='staff_login')
def edit_scheme(request, scheme_id):
    """ Staff can edit existing schemes """
    scheme = get_object_or_404(Scheme, id=scheme_id)

    if request.method == "POST":
        scheme.title = request.POST.get("title")
        scheme.eligibility = request.POST.get("eligibility")
        scheme.category = request.POST.get("category")
        scheme.link = request.POST.get("link")
        scheme.save()
        messages.success(request, "✅ Scheme updated successfully!")
        return redirect("manage_schemes")

    return render(request, "staff/schems/edit_scheme.html", {"scheme": scheme})

@login_required(login_url='staff_login')
def delete_scheme(request, scheme_id):
    """ Staff can delete schemes """
    scheme = get_object_or_404(Scheme, id=scheme_id)

    if request.method == "POST":
        scheme.delete()
        messages.success(request, "🗑️ Scheme deleted successfully!")
        return redirect("manage_schemes")

    return render(request, "staff/schems/delete_scheme.html", {"scheme": scheme})


####################### Manage Helpdesk from Staff ########################
@login_required(login_url='staff_login')
def manage_helpdesk(request):
    """ Staff can view and manage all support requests """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    support_requests = SupportRequest.objects.all().order_by("-created_at")

    return render(request, "staff/helpdeskFaq/manage_helpdesk.html", {
        "support_requests": support_requests
    })

@login_required(login_url='staff_login')
def contact_citizen(request, request_id):
    """ Staff can contact citizens via email based on their support request """
    support_request = get_object_or_404(SupportRequest, id=request_id)

    if request.method == "POST":
        reply_message = request.POST.get("reply_message")

        # Send email to citizen (Django Email)
        send_mail(
            subject="Response to Your Support Request",
            message=f"Dear {support_request.name},\n\n{reply_message}\n\nBest regards,\nPanchayat Support Team",
            from_email="support@panchayatapp.com",
            recipient_list=[support_request.email],
            fail_silently=False,
        )

        # Mark request as "Resolved"
        support_request.status = "Resolved"
        support_request.save()

        messages.success(request, "📩 Response sent to citizen successfully!")
        return redirect("manage_helpdesk")

    return render(request, "staff/helpdeskFaq/contact_citizen.html", {"support_request": support_request})

@login_required(login_url='staff_login')
def resolve_support_request(request, request_id):
    helpdesk_request = get_object_or_404(SupportRequest, id=request_id)

    if request.method == "POST":
        response_text = request.POST.get("response")
        helpdesk_request.response = response_text
        helpdesk_request.status = "Resolved"
        helpdesk_request.save()

        # ✅ Notify user
        Notification.objects.create(
            user=helpdesk_request.user,
            message="Your helpdesk request has been resolved. Check the response now!",
            notification_type="success",
            related_object_id=helpdesk_request.id
        )

        messages.success(request, "Helpdesk request resolved successfully.")
        return redirect("manage_helpdesk")

    return render(request, "staff/helpdesk/respond.html", {"helpdesk_request": helpdesk_request})

@login_required(login_url='staff_login')
def manage_faqs(request):
    """ Staff can manage all FAQs """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    faqs = FAQ.objects.all()

    return render(request, "staff/helpdeskFaq/manage_faqs.html", {"faqs": faqs})


@login_required(login_url='staff_login')
def add_faq(request):
    """ Staff can add FAQs """
    if request.method == "POST":
        question = request.POST.get("question")
        answer = request.POST.get("answer")

        if question and answer:
            FAQ.objects.create(question=question, answer=answer)
            messages.success(request, "✅ FAQ added successfully!")
            return redirect("manage_faqs")

    return render(request, "staff/helpdeskFaq/add_faq.html")


@login_required(login_url='staff_login')
def edit_faq(request, faq_id):
    """ Staff can edit FAQs """
    faq = get_object_or_404(FAQ, id=faq_id)

    if request.method == "POST":
        faq.question = request.POST.get("question")
        faq.answer = request.POST.get("answer")
        faq.save()
        messages.success(request, "✅ FAQ updated successfully!")
        return redirect("manage_faqs")

    return render(request, "staff/helpdeskFaq/edit_faq.html", {"faq": faq})

@login_required(login_url='staff_login')
def delete_faq(request, faq_id):
    """ Staff can delete FAQs """
    faq = get_object_or_404(FAQ, id=faq_id)

    if request.method == "POST":
        faq.delete()
        messages.success(request, "🗑️ FAQ deleted successfully!")
        return redirect("manage_faqs")

    return render(request, "staff/helpdeskFaq/delete_faq.html", {"faq": faq})



##################### Job Opportunities Views #####################
@login_required(login_url='staff_login')
def job_opportunities(request):
    """ Staff can manage job listings """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    jobs = JobOpportunity.objects.all()
    return render(request, "staff/jobs/job_opportunities.html", {"jobs": jobs})


@login_required(login_url='staff_login')
def add_job(request):
    if request.method == "POST":
        job_title = request.POST.get("job_title")
        company_name = request.POST.get("company_name")
        location = request.POST.get("location")
        salary = request.POST.get("salary")
        description = request.POST.get("description")
        contact_email = request.POST.get("contact_email")  # ✅ Get email from form

        JobOpportunity.objects.create(
            job_title=job_title,
            company_name=company_name,
            location=location,
            salary=salary,
            description=description,
            contact_email=contact_email  # ✅ Save email in database
        )

        # ✅ Notify all users about new job opportunity
        users = User.objects.all()
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"New Job Opportunity: {job_title} at {company_name}! Apply now.",
                notification_type="info",
                related_object_id=job_title.id
            )

        messages.success(request, "✅ Job opportunity added successfully!")
        return redirect("job_opportunities")

    return render(request, "staff/jobs/add_job.html")


@login_required(login_url='staff_login')
def delete_job(request, job_id):
    """ Staff can delete a job opportunity. """
    job = get_object_or_404(JobOpportunity, id=job_id)

    if request.method == "POST":
        job.delete()
        messages.success(request, "🗑 Job opportunity deleted successfully!")
        return redirect("job_opportunities")

    return render(request, "staff/jobs/delete_job.html", {"job": job})


##################### Local Tourism Views #####################
@login_required(login_url='staff_login')
def tourism_management(request):
    """ Staff can manage tourism listings """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    places = LocalTourism.objects.all()
    return render(request, "staff/tourism/tourism_management.html", {"places": places})


@login_required(login_url='staff_login')
def add_tourism(request):
    """ Staff can add tourism places """
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        location = request.POST.get("location")
        best_time_to_visit = request.POST.get("best_time_to_visit")
        contact_info = request.POST.get("contact_info")

        if name and location:
            LocalTourism.objects.create(
                name=name,
                description=description,
                location=location,
                best_time_to_visit=best_time_to_visit,
                contact_info=contact_info
            )
            messages.success(request, "New tourism spot added successfully!")
            return redirect("tourism_management")

    return render(request, "staff/tourism/add_tourism.html")


@login_required(login_url='staff_login')
def delete_tourism(request, tourism_id):
    """ Staff can delete tourism places """
    place = get_object_or_404(LocalTourism, id=tourism_id)
    place.delete()
    messages.success(request, "Tourism spot deleted successfully!")
    return redirect("tourism_management")


##################### Village Statistics Views #####################
@login_required(login_url='staff_login')
def manage_village_dashboard(request):
    """ Staff can manage the village dashboard (stats & updates) """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    village_stats = VillageDashboard.objects.first()  # ✅ Get village stats
    updates = VillageUpdate.objects.all().order_by("-created_at")  # ✅ Get all updates

    if request.method == "POST":
        if "add_update" in request.POST:  # ✅ Handling new updates
            title = request.POST.get("title")
            description = request.POST.get("description")
            if title and description:
                VillageUpdate.objects.create(title=title, description=description)
                messages.success(request, "✅ New update added successfully!")
                return redirect("manage_village_dashboard")

        else:  # ✅ Handling Village Statistics Update
            village_stats.population = request.POST.get("population")
            village_stats.literacy_rate = request.POST.get("literacy_rate")
            village_stats.ongoing_projects = request.POST.get("ongoing_projects")
            village_stats.annual_budget = request.POST.get("annual_budget")
            village_stats.village_location = request.POST.get("village_location")
            village_stats.employment_rate = request.POST.get("employment_rate")
            village_stats.save()
            messages.success(request, "✅ Village statistics updated successfully!")
            return redirect("manage_village_dashboard")

    context = {
        "village_stats": village_stats,
        "updates": updates
    }
    return render(request, "staff/dashboard/manage_village_dashboard.html", context)

@login_required(login_url='staff_login')
def delete_village_update(request, update_id):
    """ Staff can delete a village update """
    update = get_object_or_404(VillageUpdate, id=update_id)
    update.delete()
    messages.success(request, "🗑 Village update deleted successfully!")
    return redirect("manage_village_dashboard")

##################### Panchayat Members Views #####################
@login_required(login_url='staff_login')
def manage_panchayat(request):
    """ Staff can manage Panchayat members """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    members = PanchayatMember.objects.all()
    return render(request, "staff/profiles/manage_panchayat_profiles.html", {"members": members})

@login_required(login_url='staff_login')
def add_panchayat_member(request):
    """ Staff can add Panchayat members """
    if request.method == "POST":
        name = request.POST.get("name")
        role = request.POST.get("role")
        phone_number = request.POST.get("phone_number")
        image_url = request.POST.get("image_url")

        if name and role:
            PanchayatMember.objects.create(name=name, role=role, phone_number=phone_number, image_url=image_url)
            messages.success(request, "✅ Panchayat member added successfully!")
            return redirect("manage_panchayat")

    return render(request, "staff/profiles/add_panchayat_member.html")

@login_required(login_url='staff_login')
def delete_panchayat_member(request, member_id):
    """ Staff can delete Panchayat members """
    member = get_object_or_404(PanchayatMember, id=member_id)

    if request.method == "POST":
        member.delete()
        messages.success(request, "Panchayat member deleted successfully!")
        return redirect("manage_panchayat")

    return render(request, "staff/profiles/delete_panchayat_member.html", {"member": member})

@login_required(login_url='staff_login')
def edit_panchayat_member(request, member_id):
    """ Staff can edit Panchayat members """
    member = get_object_or_404(PanchayatMember, id=member_id)

    if request.method == "POST":
        member.name = request.POST.get("name", member.name)
        member.role = request.POST.get("role", member.role)
        member.phone_number = request.POST.get("phone_number", member.phone_number)
        member.image_url = request.POST.get("image_url", member.image_url)
        member.save()
        messages.success(request, "✅ Panchayat member updated successfully!")
        return redirect("manage_panchayat")

    return render(request, "staff/profiles/edit_panchayat_member.html", {"member": member})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import GalleryImage

# ✅ User-side gallery
@login_required(login_url='login_view')
def user_gallery(request):
    images = GalleryImage.objects.all().order_by("-uploaded_at")
    return render(request, 'user/Photo_Gallery/gallery.html', {"images": images})

# ✅ Staff can manage gallery images
@login_required(login_url='staff_login')
def manage_gallery(request):
    """Staff can manage the gallery images"""
    user_profile = UserProfile.objects.get(user=request.user)  # ✅ Explicitly fetch UserProfile
    
    if user_profile.user_type != "staff":
        return redirect("dashboard_view")

    images = GalleryImage.objects.all().order_by("-uploaded_at")
    return render(request, "staff/photoGallery/manage_gallery.html", {"images": images})

# ✅ Staff can add images (Without Forms.py)
@login_required(login_url='staff_login')
def add_gallery_image(request):
    if request.method == "POST":
        title = request.POST.get("title")
        image = request.FILES.get("image")

        if title and image:
            GalleryImage.objects.create(title=title, image=image)
            messages.success(request, "✅ Image added successfully!")
            return redirect("manage_gallery")
        else:
            messages.error(request, "❌ Title and Image are required!")

    return render(request, "staff/photoGallery/add_gallery_image.html")

# ✅ Staff can delete images
@login_required(login_url='staff_login')
def delete_gallery_image(request, image_id):
    image = get_object_or_404(GalleryImage, id=image_id)
    image.delete()
    messages.success(request, "🗑 Image deleted successfully!")
    return redirect("manage_gallery")


####################### Staff Survey Management ########################
@login_required(login_url='staff_login')
def manage_surveys(request):
    """ Staff can manage all surveys & view user feedback """
    surveys = Survey.objects.all().order_by('-created_at')

    # ✅ Fetch user feedback instead of survey responses
    survey_feedbacks = Feedback.objects.all().order_by("-submitted_at")  # ✅ Fix applied


    return render(request, "staff/surveys/manage_surveys.html", {
        "surveys": surveys,
        "survey_feedbacks": survey_feedbacks,  # ✅ Corrected to use Feedback model
    })

@login_required(login_url='staff_login')
def add_survey(request):
    """ Staff can add new surveys """
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        if title and description:
            Survey.objects.create(title=title, description=description)
            messages.success(request, "✅ New Survey Added Successfully!")
            return redirect("manage_surveys")

    return render(request, "staff/surveys/add_survey.html")


@login_required(login_url='staff_login')
def toggle_survey_status(request, survey_id):
    """ Staff can activate or close a survey dynamically """
    survey = get_object_or_404(Survey, id=survey_id)
    survey.is_active = not survey.is_active  # ✅ Toggle status
    survey.save()

    if survey.is_active:
        messages.success(request, "✅ Survey is now Active!")
    else:
        messages.warning(request, "🚫 Survey has been Closed!")

    return redirect("manage_surveys")

@login_required(login_url='staff_login')
def delete_survey(request, survey_id):
    """ Staff can delete a survey """
    survey = get_object_or_404(Survey, id=survey_id)

    if request.method == "POST":
        survey.delete()
        messages.success(request, "🗑️ Survey Deleted Successfully!")
        return redirect("manage_surveys")

    return render(request, "staff/surveys/delete_survey.html", {"survey": survey})


@login_required(login_url='staff_login')
def view_survey_responses(request, survey_id):
    """ Staff can view responses for a specific survey """
    survey = get_object_or_404(Survey, id=survey_id)
    responses = SurveyResponse.objects.filter(survey=survey)

    return render(request, "staff/surveys/view_responses.html", {"survey": survey, "responses": responses})


@login_required(login_url='staff_login')
def manage_feedback(request):
    """ Staff can view feedback submitted by citizens """
    feedbacks = Feedback.objects.all().order_by("-submitted_at")  # ✅ Ensure correct data retrieval

    return render(request, "staff/surveys/manage_feedback.html", {"feedbacks": feedbacks})


@login_required(login_url='staff_login')
def delete_feedback(request, feedback_id):
    """ Staff can delete feedback if necessary """
    feedback = get_object_or_404(Feedback, id=feedback_id)

    if request.method == "POST":
        feedback.delete()
        messages.success(request, "🗑️ Feedback Deleted Successfully!")
        return redirect("manage_feedback")

    return render(request, "staff/surveys/delete_feedback.html", {"feedback": feedback})
