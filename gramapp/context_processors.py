from django.utils.translation import get_language, activate

def language_context(request):
    """ Ensure templates always get the correct active language """
    stored_language = request.session.get('django_language') or request.COOKIES.get('django_language')
    
    if stored_language and stored_language != get_language():
        activate(stored_language)  # ✅ Force activate the stored language

    return {
        "current_language": get_language(),  # ✅ Pass active language to templates
    }

from django.contrib.auth.decorators import login_required
from .models import UserProfile

def user_profile_context(request):
    """ Adds user profile details to all templates """
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = None  # Handle missing profiles gracefully
    else:
        user_profile = None

    return {"user_profile": user_profile}
