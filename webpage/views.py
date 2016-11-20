# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from datetime import datetime
from intranet.models import Document
from webpage.models import Section, News
from webpage.forms import ImageForm
import json

# Create your views here.

def home(request):
	documents = Document.objects.filter(type=False)[:3]
	return render(request, 'webpage/home.html', {
							'current_view': 'home',
							'documents': documents,
							'body': 'inicio',
							'header': News.objects.exclude(header="").exclude(header=None)[:5],
							'news_1': News.objects.exclude(thumbnail="").exclude(thumbnail=None)[:2],
							'news_2': News.objects.exclude(thumbnail="").exclude(thumbnail=None)[2:4],
							})


def about(request, sub=None):
	if sub == 'us':
		return render(request, 'webpage/about/us.html', {'current_view': 'about', 'body': 'seccion'})
	elif sub == 'history':
		return render(request, 'webpage/about/history.html', {'current_view': 'about', 'body': 'seccion'})
	else:
		return render(request, 'webpage/about.html', {'current_view': 'about', 'body': 'seccion', 'section': Section.objects.filter(slug="about").first()})


def research(request):
	return render(request, 'webpage/research.html', {'current_view': 'research', 'body': 'seccion'})


def members(request):
	return render(request, 'webpage/members.html', {'current_view': 'members', 'body': 'seccion'})

def news_feed(request):
	return render(request, 'webpage/news_feed.html', {'current_view': 'news', 'body': 'blog'})

def news_editor(request, id = None):
	if request.user.is_authenticated():
		news = News.objects.filter(id=id)
		if news:
			news = news[0]
			if request.method == "GET":
				# Si la noticia corresponde al usuario o es un administrador se permite el acceso
				if news.author == request.user or request.user.is_admin:
					if news:
						return render(request, 'webpage/news_editor.html', {'current_view': 'news', 'body': 'blog', 'news': news})
				else:
					return HttpResponseRedirect(reverse('webpage:home')) # 'No tienes permiso para modificar esta noticia'
			elif request.method == "POST":
				# En este caso la respuesta sera en un objeto JSON
				if request.POST.get('news-title-html') is not None:
					news.title_html = request.POST.get('news-title-html')
				if request.POST.get('news-title') is not None:
					news.title = request.POST.get('news-title')
				if request.POST.get('news-content') is not None:
					news.body = request.POST.get('news-content')
				news.save()
				return JsonResponse({'error': False})
		else:
			# La noticia no existe
			# Deberia enviar al feed de noticias o a una pagina 404
			return HttpResponseRedirect(reverse('webpage:home'))

	else:
		return HttpResponseRedirect(reverse('webpage:home'))

def news(request, year = None, month = None, day = None, title = None):
	try:
		date =  datetime.strptime(str(day) + str(month) + str(year), '%d%m%Y')
		news = News.objects.filter(date=date, slug=title)
		if news:
			return render(request, 'webpage/news.html', {'current_view': 'news', 'body': 'blog', 'news_': news[0]})
		else:
			return HttpResponseRedirect(reverse('webpage:news_feed'))
	except:
		return HttpResponseRedirect(reverse('webpage:news_feed'))

def save_images(request):
	if request.user.is_authenticated() and request.method == 'POST':
		info = json.loads(request.POST.get('info'))
		news = News.objects.filter(id=info['news_id'])
		if news:
			if news[0].author == request.user or request.user.is_admin:
				response = []
				for key in request.FILES:
					fields = {
							'news': info['news_id']
						}
					files = {
							'picture': request.FILES[key]
						}
					form = ImageForm(fields, files)
					if form.is_valid():
						image = form.save()
						image.set_filename()
						response.append({'client_side_id': key, 'url':image.static_url()})
					else:
						return JsonResponse({'error': True, 'message': form.errors})
				return JsonResponse({'error': False, 'urls': response})
			else:
				return JsonResponse({'error': True, 'message': _("No tienes permisos para modificar esta noticia")})
		else:
			return JsonResponse({'error': True, 'message': _("Esta noticia no existe")})
	else:
		return JsonResponse({'error': True, 'urls': _(u"Debes iniciar sesión")})