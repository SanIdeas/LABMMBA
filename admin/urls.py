from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^invitation/', views.sendInvitation, name="invitation"),
    url(r'^users/$', views.users, name="users"),
    url(r'^users/profile/(?P<user_id>.*)/$', views.users, {'profile': True}, name="profile"),
    url(r'^users/unblock/(?P<user_id>.*)$', views.users, {'unblock': True}, name='unblock_user'),
    url(r'^users/block/(?P<user_id>.*)$', views.users, {'block': True}, name='block_user'),
    url(r'^users/delete/(?P<user_id>.*)$', views.users, {'delete': True}, name='delete_user'),
    url(r'^users/activate/(?P<user_id>.*)$', views.users, {'activate': True}, name='activate_user'),
    url(r'^documents/$', views.documents, name="documents"),
    url(r'^search/(?P<search>.*)/$', views.documents, name="admin_search"),
    url(r'^areas/$', views.areas, name="areas"),
    url(r'^areas/edit/(?P<area_id>.*)$', views.areas, name='edit_area'),
    url(r'^areas/delete/(?P<area_id>.*)$', views.areas, name='delete_area'),
    url(r'^subareas/edit/(?P<subarea_id>.*)$', views.areas, name='edit_subarea'),
    url(r'^subareas/delete/(?P<subarea_id>.*)$', views.areas, name='delete_subarea'),
    url(r'^webpage/$', views.webpage, name="webpage"),
    url(r'^webpage/edit/(?P<section_id>.*)$', views.webpage, name='edit_section'),
    url(r'^webpage/images/$', views.save_images, name="save_images"),
    url(r'^webpage/headers/$', views.upload_header, name="upload_section_header"),
    url(r'^news/$', views.news, name="news"),
    url(r'^news/publish/(?P<news_id>.*)$', views.news, {'publish': True}, name='publish_news'),
    url(r'^news/unpublish/(?P<news_id>.*)$', views.news, {'unpublish': True}, name='unpublish_news'),
    url(r'^news/show_header/(?P<news_id>.*)$', views.news, {'show_header': True}, name='show_header_news'),
    url(r'^news/hide_header/(?P<news_id>.*)$', views.news, {'hide_header': True}, name='hide_header_news'),
]