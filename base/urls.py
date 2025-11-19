from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from decouple import config

urlpatterns = [
    # admin pannel
    path('admin/', admin.site.urls),

    # package
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # api
    path("v1/api/auth/",  include("apis.v1.auth.urls", namespace="v1_auth")),
    path("v1/api/course/", include("apis.v1.course.urls", namespace="v1_course")),
    path('v1/api/subscription/', include("apis.v1.subscription.urls", namespace="v1_subscription")),
]

SHOW_DEBUGGER_TOOLBAR = config("SHOW_DEBUGGER_TOOLBAR", cast=bool, default=True)
if SHOW_DEBUGGER_TOOLBAR:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()

admin.site.site_header = _('پنل مدیریت سیستم')
admin.site.site_title = _('مدیریت')
admin.site.index_title = _('مدیریت سیستم')