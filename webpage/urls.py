from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.home, name="home"),
	url(r'^news/$', views.news_feed, name="news_feed"),
	url(r'^news/images/$', views.save_images, name="save_images"),
	url(r'^news/comment/$', views.new_news_comment, name="new_news_comment"),
	url(r'^news/edit/(?P<id>.*)/$', views.news_editor, name="news_editor"),
	url(r'^news/(?P<year>.*)/(?P<month>.*)/(?P<day>.*)/(?P<title>.*)/$', views.news, name="news"),
	url(r'^news/(?P<id>.*)/$', views.news, name="news"),
	url(r'^events/$', views.events_feed, name="events_feed"),
	url(r'^event/(?P<title>.*)/$', views.event, name="event"),
	url(r'^about/gallery/$', views.gallery, name="gallery"),
	url(r'^(?P<section_slug>.*)/(?P<subsection_slug>.*)/$', views.section, name="subsection"),
	url(r'^(?P<section_slug>.*)/$', views.section, name="section")
]