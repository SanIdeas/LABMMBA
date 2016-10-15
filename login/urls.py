from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.login, name="login"),
    url(r'logout/', views.logout, name="logout"),
    url(r'signup/', views.signup, name="signup"),
    url(r'register/$', views.register, name="register"),
    url(r'register/(?P<token>.*)/$', views.register, name="register")
]
