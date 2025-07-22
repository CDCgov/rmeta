
from django.contrib import admin
from django.urls import path, include
from django.urls import re_path as url
from oauth2_provider import views as oauth2_views
from apps.report_metadata.views import home, request_access
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from .utils import IsAppInstalled
admin.site.site_header = "CDC Meta Admin"
admin.site.site_title = "CDC Meta Admin Portal"
admin.site.index_title = "CDC Meta Administration"


oauth2_base_urlpatterns = [
    url(r"^authorize/$",
        oauth2_views.AuthorizationView.as_view(),
        name="authorize"),
    url(r"^token/$",
        oauth2_views.TokenView.as_view(),
        name="token"),
    url(r"^revoke_token/$",
        oauth2_views.RevokeTokenView.as_view(),
        name="revoke-token"),
    url(r"^introspect/$",
        oauth2_views.IntrospectTokenView.as_view(),
        name="introspect"),
]


oauth2_management_urlpatterns = [
    # Application management views
    url(r"^applications/$",
        oauth2_views.ApplicationList.as_view(),
        name="list"),
    url(r"^applications/register/$",
        oauth2_views.ApplicationRegistration.as_view(),
        name="register"),
    url(r"^applications/(?P<pk>[\w-]+)/$",
        oauth2_views.ApplicationDetail.as_view(),
        name="detail"),
    url(r"^applications/(?P<pk>[\w-]+)/delete/$",
        oauth2_views.ApplicationDelete.as_view(),
        name="delete"),
    url(r"^applications/(?P<pk>[\w-]+)/update/$",
        oauth2_views.ApplicationUpdate.as_view(),
        name="update"),
    # Token management views
    url(r"^authorized_tokens/$",
        oauth2_views.AuthorizedTokensListView.as_view(),
        name="authorized-token-list"),
    url(r"^authorized_tokens/(?P<pk>[\w-]+)/delete/$",
        oauth2_views.AuthorizedTokenDeleteView.as_view(),
        name="authorized-token-delete"),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dq/', include('apps.dq.urls')),
    path('mdn/', include('apps.mdn.urls')),
    path('sophv/', include('apps.sophv.urls')),
    path('roster/', include('apps.roster.urls')),
    path('anonymouser/', include('apps.anonymouser.urls')),
    path('reporting/', include('apps.report_metadata.urls')),
    # 3rd party
    url('social-auth/', include('social_django.urls', namespace='social')),
    path('o/',include((oauth2_management_urlpatterns + oauth2_base_urlpatterns, 'oauth2_provider'))),
    
    # Other URL
    #path('public/api/v1/', include('apps.report_metadata.publicapi_urls')),
    #path('hashcow/', include('apps.hashcow.urls')),
    
    path('', home, name='home' ),
    path('accounts/login/', ratelimit(key='ip', rate='100/h')(LoginView.as_view(
            template_name='report_metadata/login.html'
        )), name='login'),
    path('accounts/logout', LogoutView.as_view(
            template_name='report_metadata/logged-out.html'
        ), name='logout'),
    path('accounts/request-access', request_access, name='request_access'),
    path('accounts/change-password', PasswordChangeView.as_view(
            template_name='report_metadata/change-password.html'
        ), name='password_change'),
    path('accounts/change-password-done', PasswordChangeDoneView.as_view(
            template_name='report_metadata/change-password-done.html'
        ), name='password_change_done'),

    path("accounts/", include("django.contrib.auth.urls")),
]

