from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language  # ✅ Add this

urlpatterns = [
    path('admin/', admin.site.urls),
    path('set-language/', set_language, name='switch_language'),  # ✅ Add this for language switching
]

# ✅ Wrap app URLs inside `i18n_patterns` to support translations
urlpatterns += i18n_patterns(
    path('', include('gramapp.urls')),
    prefix_default_language=False  # ✅ Avoid showing default language (like /en/)
)

# ✅ Serve media files during development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
