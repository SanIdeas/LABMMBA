# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import javascript_catalog

urlpatterns = [
	url(r'^jsi18n/$', javascript_catalog,  name='javascript-catalog'),
    url(r'^crossref/', include('crossref.urls', namespace="crossref")),
]

urlpatterns += i18n_patterns(
    url(r'^', include('home.urls')),
    url(r'^about/', include('about.urls')),
    url(r'^intranet/', include('intranet.urls', namespace="intranet")),
    url(r'^login/', include('login.urls')),
    url(r'^publications/', include('public_search.urls')),
    url(r'^drive/', include('drive.urls')),
)
