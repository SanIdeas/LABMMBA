from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.login, name="login"),
    url(r'logout/', views.logout, name="logout"),
    url(r'register/$', views.register, name="register"),
    url(r'register/(?P<token>.*)/$', views.register, name="register"),
    url(r'password/change/$', views.change_password, name="change_password"),
    url(r'password/recover/$', views.recover_password, name="recover_password"),
    url(r'password/recover/callback/$', views.recover_password_callback, name="recover_password_callback"),
    url(r'password/recover/callback/(?P<token>.*)/$', views.recover_password_callback, name="recover_password_callback")
]
