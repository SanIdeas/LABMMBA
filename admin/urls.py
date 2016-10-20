from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'invitation/', views.sendInvitation, name="invitation"),
    url(r'users/$', views.users, name="users"),
    url(r'users/profile/(?P<user_id>.*)/$', views.users, {'profile': True}, name="profile"),
    url(r'users/unblock/(?P<user_id>.*)$', views.users, {'unblock': True}, name='unblock_user'),
    url(r'users/block/(?P<user_id>.*)$', views.users, {'block': True}, name='block_user'),
    url(r'users/delete/(?P<user_id>.*)$', views.users, {'delete': True}, name='delete_user'),
    url(r'users/activate/(?P<user_id>.*)$', views.users, {'activate': True}, name='activate_user'),
]