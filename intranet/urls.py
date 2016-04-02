from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="intranet"),
    url(r'^profile/', views.profile, name="profile"),
    url(r'^upload/', views.upload, name='upload'),
]
