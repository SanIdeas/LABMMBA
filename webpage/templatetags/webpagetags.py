from django import template
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve
from django.utils import translation
import re
from django.utils.translation import ugettext as _

register = template.Library()



@register.filter
def format_date(dates):
	year = dates[0][0].year
	diferents_years = False
	for month in dates:
		if year != month[0].year:
			diferents_years = True

	date = ""
	for month in range(0, len(dates)):
		for day in range(0, len(dates[month])):
			if day == len(dates[month])-1:
				date = date + str(dates[month][day].day)
			else:
				date = date + str(dates[month][day].day) + ', '
		date = date +_(' de %s') % _(dates[month][0].strftime("%B"))
		if diferents_years and month != len(dates)-1:
			date = date + _(' de %s') % dates[month][0].year + ' - '
		elif not diferents_years and month != len(dates)-1:
			date = date + ' - '
		elif month == len(dates)-1:
			date = date + _(' de %s') % dates[month][0].year
	return date
