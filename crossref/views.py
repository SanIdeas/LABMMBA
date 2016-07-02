# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.utils.translation import ugettext as _
from habanero import Crossref
import sys, time


# Create your views here.

def query(request, query=None):
	if request.user.is_authenticated() == True:
		cr = Crossref()
		result = cr.works(query=query)['message']['items']
		response = []
		count = 0
		for r in result:
			if count == 10:
				break;
			try: 
				title = r['title'][0].encode(sys.stdout.encoding, errors='replace')
			except:
				title = None
			if title:#Si existe titulo el documento se añade a la respuesta. De lo contrario se salta.
				timestamp = time.gmtime(int(r['created']['timestamp'])/1000)
				r['date'] = time.strftime('%Y-%m-%d', timestamp)
				r['year'] = timestamp.tm_year
				response.append(r)
				count  = count + 1
				#if 'author' in r:
				#	given = r['author'][0]['given'] if 'given' in r['author'][0] else ''
				#	family = r['author'][0]['family'] if 'family' in r['author'][0] else ''
				#if 'page' in r:
				#	page = r['page']
				#if 'created' in r:
				#	timestamp = time.gmtime(int(r['created']['timestamp'])/1000)
				#	date = time.strftime('%Y-%m-%d', timestamp)
				#row = '<li class="crossref-row"'
				#print title
				#if 'author' in r:
				#	row = row + 'author="' + given + ' ' + family + '"'
				#if 'page' in r:
				#	row = row + 'pages="' + page + '"'
				#if 'created' in r:
				#	row = row + 'date="' + date + '"'
				#	print '- year: ', timestamp.tm_year
				#row = row + 'issn="' + r['issn'][0] + '"'
				#row = row + 'url="' + r['url'] + '"'
				#row = row + 'doi="' + r['DOI'] + '"'
				#row = row + '>\n'
				#response = reponse + row
		return render(request, 'crossref/template.html', {'documents': response})
	else:
		return JsonResponse({'error': True, 'message':  _('Debe iniciar sesion.')})

