from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import LoginView, LogoutView
from users.admin import custom_admin_site

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/users/', include('users.urls')),
]