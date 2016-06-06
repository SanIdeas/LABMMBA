from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="intranet"),
    url(r'documents/$', views.documents, name="documents"),
    url(r'search/(?P<search>.*)/$', views.documents, name="intranet_search"),
    url(r'^profile/$', views.profile, name="profile"),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^viewer/(?P<author>.*)/(?P<title>.*)/$', views.pdf_viewer, name='viewer'),
    url(r'^profile/update/picture/$', views.update_profile_picture, name='update_picture'),
    url(r'^profile/(?P<user_id>.*)/$', views.profile, name='profile'),
    url(r'^users/$', views.users, name='users'),
    url(r'^document/(?P<author>.*)/(?P<title>.*)/', views.document, name="document"),
    url(r'^helper/(?P<search>.*)/$', views.search_helper, name="helper"),
]
