import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings


from django import template
 
register = template.Library()
 
@register.inclusion_tag(settings.ANALYTICS_HTML_DIR, takes_context=True)
def analytics(context, next = None):

	# The scope for the OAuth2 request.
	SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
	credentials = ServiceAccountCredentials.from_json_keyfile_name( settings.ANALYTICS_JSON_DIR , SCOPE)
	ANALYTICS_VIEW_ID = '135953807'
	ANALYTICS_VIEW_ID_PUBLIC = '135963610'


	return {
		'token': credentials.get_access_token().access_token,
		'view_id': ANALYTICS_VIEW_ID,
		'view_id_public': ANALYTICS_VIEW_ID_PUBLIC
	}