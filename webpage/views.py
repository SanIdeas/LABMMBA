from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from intranet.models import Document

# Create your views here.

def home(request):
	documents = Document.objects.filter(type=False)[:3]
	return render(request, 'webpage/home.html', {'current_view': 'home', 'documents': documents, 'body': 'inicio'})

def about(request, sub = None):
	if sub == 'us':
		return render(request, 'webpage/about/us.html', {'current_view': 'about', 'body': 'seccion'})
	elif sub == 'history':
		return render(request, 'webpage/about/history.html', {'current_view': 'about', 'body': 'seccion'})
	else:
		return render(request, 'webpage/about.html', {'current_view': 'about', 'body': 'seccion'})

def research(request):
	return render(request, 'webpage/research.html', {'current_view': 'research', 'body': 'seccion'})

def members(request):
	return render(request, 'webpage/members.html', {'current_view': 'members', 'body': 'seccion'})