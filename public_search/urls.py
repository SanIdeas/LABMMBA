from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.search, name="publications"),
    url(r'search/(?P<search>.*)/$', views.search, name="public_search"),

]
