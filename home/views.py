from django.shortcuts import render
from django.http import HttpResponse
from intranet.models import Document

# Create your views here.

def home(request):
	documents = Document.objects.filter(type=False)[:3]
	return render(request, 'home/home.html', {'current_view': 'home', 'documents': documents})