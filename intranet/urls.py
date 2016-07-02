from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^document/(?P<author>.*)/(?P<title>.*)/$', views.document, name="document"),
    url(r'^edit/document/(?P<author>.*)/(?P<title>.*)/$', views.edit_document, name="edit_document"),
    url(r'^$', views.home, name="home"),
    url(r'^documents/$', views.documents, name="documents"),
    url(r'^search/(?P<search>.*)/$', views.documents, name="intranet_search"),
    url(r'^profile/$', views.profile, name="profile"),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^viewer/(?P<author>.*)/(?P<title>.*)/$', views.pdf_viewer, name='viewer'),
    url(r'^profile/update/picture/$', views.update_profile_picture, name='update_picture'),
    url(r'^profile/(?P<user_id>.*)/$', views.profile, name='profile'),
    url(r'^users/', views.users, name='users'),
    url(r'^admin/(?P<setup>.*)/$', views.admin, name='admin_setup'),
    url(r'^admin/$', views.admin, name='admin'),
    url(r'^helper/(?P<search>.*)/$', views.search_helper, name="helper"),
]
