from django import template
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve
from django.utils import translation
import re

register = template.Library()



@register.simple_tag(name='translate_url', takes_context=True)
def do_translate_url(context,lang):
	if lang == 'es':
		current = 'en'
	else:
		current = 'es'
	regex = re.compile(r"^\/" + current + "\/")
	return regex.sub('/' + lang + '/', context['request'].get_full_path())