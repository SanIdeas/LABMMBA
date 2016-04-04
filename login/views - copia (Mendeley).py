from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from login.models import User, Area
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from mendeley import Mendeley
from mendeley.session import MendeleySession
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.templatetags.staticfiles import static

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

			# These values should match the ones supplied when registering your application.
			mendeley = Mendeley(2906, client_secret='OyGYZAJqk5B5aOp3', redirect_uri='http:/192.168.50.13:8000/intranet')

			auth = mendeley.start_implicit_grant_flow()

			# The user needs to visit this URL, and log in to Mendeley.
			login_url = auth.get_login_url()

			
			print login_url
			#Se ingresa al formulario de Mendeley
			chrome_driver = static('chrome_driver/chromedriver.exe')
			driver = driver = webdriver.Chrome("C:/chromedriver.exe") 

			driver.get(login_url)
			elem = driver.find_element_by_name("username")
			elem.send_keys("hernan.herreros.13@sansano.usm.cl")
			elem = driver.find_element_by_name("password")
			elem.send_keys("samantha")
			elem.send_keys(Keys.RETURN)
			assert "No results found." not in driver.page_source
			driver.close()
			# After logging in, the user will be redirected to a URL, auth_response.
			session = auth.authenticate(auth_response)

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