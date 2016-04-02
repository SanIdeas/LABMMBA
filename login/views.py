from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from login.models import User, Area
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

# Create your views here.

def login(request):
	if request.method == "GET":
		if request.user.is_authenticated() == False: #Si el usuario ya esta logueado no podra ingresar a la vista Login. Se redirecciona a Intranet.
			return render(request, 'login/login.html')
		else:
			return HttpResponseRedirect(reverse('intranet')) #Se redirecciona a la ultima pagina visitada.			
	else:
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(username=email, password=password)
		if user is not None: #Si el usuario es autenticado se inicia sesion.
			auth_login(request, user)
			return HttpResponseRedirect(reverse('intranet'))
		else:
			return render(request, 'login/login.html')

def signin(request):
	if request.user.is_authenticated() == False: #Si el usuario ya esta logueado no podra ingresar a la vista Login. Se redirecciona a Intranet.
			if request.method == "GET":
				return render(request, 'login/signin.html', {'areas': Area.objects.all()})
			else:
				try:
				    user = User.objects.get(email=request.POST['email'])
				except User.DoesNotExist:
				    user = None

				if user is  None:
					user = User.objects.create_user(request.POST['email'], request.POST['first_name'], request.POST['last_name'], request.POST['institution'], request.POST['country'], Area.objects.get(id=request.POST['area']), request.POST['career'], request.POST['password'])
					user = authenticate(username=request.POST['email'], password=request.POST['password'])
					auth_login(request, user)
					return HttpResponseRedirect(reverse('intranet'))
				else:
					return render(request, 'login/signin.html', {'areas': Area.objects.all()})
	else:
		return HttpResponseRedirect(reverse('intranet'))


def logout(request):
	if request.user.is_authenticated() is not None:
		auth_logout(request)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER')) #Se redirecciona a la ultima pagina visitada.