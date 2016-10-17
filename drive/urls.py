from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^analizer$', views.link_analizer),
    url(r'^analizer/(?P<link>.*)/$', views.link_analizer, name="link_analizer"),
    url(r'^user/$', views.user_files, name="user_files"),
    url(r'^user/(?P<folderId>.*)/$', views.user_files, name="user_files"),
    url(r'^oauth2callback/$', views.oauth2callback, name="oauth2callback"),
    url(r'^get_credentials/$', views.get_credentials, name="get_credentials"),
    url(r'^download/(?P<ids>.*)/$', views.download_drive_files, name="download_drive_files"),
]
