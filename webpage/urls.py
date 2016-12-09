from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.home, name="home"),
	url(r'^news/$', views.news_feed, name="news_feed"),
	url(r'^news/images/$', views.save_images, name="save_images"),
	url(r'^news/edit/(?P<id>.*)/$', views.news_editor, name="news_editor"),
	url(r'^news/(?P<year>.*)/(?P<month>.*)/(?P<day>.*)/(?P<title>.*)/$', views.news, name="news"),
	url(r'^(?P<section_slug>.*)/(?P<subsection_slug>.*)/$', views.section, name="subsection"),
	url(r'^(?P<section_slug>.*)/$', views.section, name="section")
]