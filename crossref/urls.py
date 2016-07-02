from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^query/(?P<query>.*)$', views.query, name="query"),
]
