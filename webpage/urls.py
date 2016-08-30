from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
 	url(r'^about/$', views.about, name="about"),
 	url(r'^about/us/$', views.about, {'sub': 'us'}, name="us"),
 	url(r'^about/history/$', views.about, {'sub': 'history'}, name="history"),
 	url(r'^members/$', views.members, name="members"),
 	url(r'^research/$', views.research, name="research"),
]
