from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.

def home(request):
	if request.user.is_authenticated() == True:
		return render(request, 'intranet/home.html', {'current_view': 'intranet'})
	else:
		return HttpResponseRedirect(reverse('login'))

def profile(request):
	if request.user.is_authenticated() == True:
		return render(request, 'intranet/profile.html', {'current_view': 'intranet'})
	else:
		return HttpResponseRedirect(reverse('login'))

def upload(request):
	if request.user.is_authenticated() == True:
		return render(request, 'intranet/upload.html', {'current_view': 'intranet'})
	else:
		return HttpResponseRedirect(reverse('login'))