from django.shortcuts import render
from django.utils.translation import activate

# Create your views here.

def about(request):
	return render(request, 'about/about.html', {'current_view': 'about', 'body': 'seccion'})