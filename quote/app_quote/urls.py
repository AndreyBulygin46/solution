from django.urls import path
from .views import register, user_login, home, delete_quote, add_quote
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete/<int:quote_id>/', delete_quote, name='delete_quote'),
    path('add/', add_quote, name='add_quote'),
]
