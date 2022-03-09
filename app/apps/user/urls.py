from django.urls import path, re_path
from apps.user import views
from rest_framework.routers import SimpleRouter


app_name = 'user'

router = SimpleRouter()

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('send-recovery-email/',
            views.SendVerificationEmailView.as_view(),
            name='send-recovery-business-email'),
    re_path(r'^recovery-password-email/(?P<uidb64>[0-9A-Za-z_\-]+)'
            r'/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            views.PasswordRecoveryValidateView.as_view(),
            name='validate-recovery-password-email'),
    path('recovery-password-email/',
            views.PasswordRecoverySetView.as_view(),
            name='recovery-set-password-email'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)'
            r'/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            views.activate, name='activate'),
]

router.register('user-profile', views.UpdateProfileViewSet, 'user-profile')

urlpatterns += router.urls
