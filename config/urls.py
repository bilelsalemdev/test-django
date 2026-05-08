from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views.generic import RedirectView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/companies/', include('apps.companies.urls')),
    path('api/clients/', include('apps.clients.urls')),
    path('api/approvals/', include('apps.approvals.urls')),
    path('api/schema/', login_required(SpectacularAPIView.as_view()), name='schema'),
    path('api/docs/', login_required(SpectacularSwaggerView.as_view(url_name='schema')), name='docs'),
]

if settings.DEBUG:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
