from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
 	url(r'^news/$', views.news_feed, name="news_feed"),
 	url(r'^news/images/$', views.save_images, name="save_images"),
 	url(r'^news/edit/(?P<id>.*)/$', views.news_editor, name="news_editor"),
 	url(r'^news/(?P<year>.*)/(?P<month>.*)/(?P<day>.*)/(?P<title>.*)/$', views.news, name="news"),
 	url(r'^about/$', views.about, name="about"),
 	url(r'^about/us/$', views.about, {'sub': 'us'}, name="us"),
 	url(r'^about/history/$', views.about, {'sub': 'history'}, name="history"),
 	url(r'^members/$', views.members, name="members"),
 	url(r'^research/$', views.research, name="research"),
]
