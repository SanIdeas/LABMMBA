from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from login.models import User, Area
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from mendeley import Mendeley
from mendeley.session import MendeleySession
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.templatetags.staticfiles import static
from login.forms import Mendeley_credentials_Form
from login.models import Mendeley_credentials
import os, datetime, base64, json, requests



# Create your views here.

def refresh_token(old_token):
	 auth_code = 'Basic ' + base64.b64encode('2906:OyGYZAJqk5B5aOp3')
	 url = 'https://api.mendeley.com/oauth/token'
	 refresh_token = old_token['refresh_token']
	 redirect_uri = 'http:/127.0.0.1:8000/login/auth_return/'
	 grant_type = 'refresh_token'
	 Content_type= 'application/x-www-form-urlencoded'

	 data = {'grant_type': grant_type, 'refresh_token': refresh_token, 'redirect_uri': redirect_uri}
	 headers = {'Authorization': auth_code, 'Content-type': Content_type}
	 request=requests.post(url, data=data, headers=headers)
	 Mendeley_credentials.objects.all().delete()
	 form = Mendeley_credentials_Form(json.loads(request.text))
	 if form.is_valid():
	 	form.save()
	 print form.errors
	 return Mendeley_credentials.objects.all()[0].get_token()

def get_mendeley_session():
	mendeley = Mendeley(2906, client_secret='OyGYZAJqk5B5aOp3', redirect_uri='http:/127.0.0.1:8000/login/auth_return/')
	token = Mendeley_credentials.objects.all()[0].get_token()
	try:
		session = MendeleySession(mendeley, token)
		print session.profiles.me.display_name
		
	except:
		print 'refresh-------------------------'
		token = refresh_token(token)
		session = MendeleySession(mendeley, token)
	#authenticator = MendeleyAuthorizationCodeAuthenticator(mendeley, token['state'])
	#refresher = MendeleyAuthorizationCodeTokenRefresher(authenticator)
	return session


def login(request):
	if request.method == "GET":
		session = get_mendeley_session()
		print '\nMendeley first name:', session.profiles.me.display_name
		search = session.documents.search('Development took place in focused chaos,')
		for doc in search.iter():
			print '----\n'
			print doc.title
			print [method for method in dir(doc) if callable(getattr(doc, method))]
		#for document in session.documents.iter():
		#	print '-', document.title
		#print '\nSession expires at: ', datetime.datetime.fromtimestamp(session.token['expires_at'])
		print '\n'
		if request.user.is_authenticated() == False: #Si el usuario ya esta logueado no podra ingresar a la vista Login. Se redirecciona a Intranet.
			return render(request, 'login/login.html')
		else:
			return HttpResponseRedirect(reverse('intranet')) #Se redirecciona a la ultima pagina visitada.			
	else:
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(username=email, password=password)
		if user is not None: 
		#Si el usuario es autenticado se inicia sesion.
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

def get_mendeley_credentials(request):
	# These values should match the ones supplied when registering your application.
	mendeley = Mendeley(2906, client_secret='OyGYZAJqk5B5aOp3', redirect_uri='http:/127.0.0.1:8000/login/auth_return/')

	auth = mendeley.start_authorization_code_flow()

	# The user needs to visit this URL, and log in to Mendeley.
	login_url = auth.get_login_url()

	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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
	url = driver.current_url
	print '1------------ session auth_return', url
	assert "No results found." not in driver.page_source
	driver.close()
	# After logging in, the user will be redirected to a URL, auth_response.
	session = auth.authenticate(url)

	session.token['state'] = auth.state
	token_old = {u'msso': u'aOXKtKYBfCJZM3WVOgPNQ02A4XJ9dLycGnfhoWJZNPApYRNQJzHsJt9K5AAKHzbO38sbkWJDnpML08vJ+MstbfhUeJMpvsC8LkAW6bFu6q3Zm9mxH5b4O10ZZBFYmiYnAr0KdNdQU8R2AVNqQPp+RCqLlMsu5O/glTdOUhZ1qLoLeBww3SPlhz0N8IYc0f1ru6T0j+VtiWeDYAOJQaKg8AgMVgO9oiwxi0cR6u+OZptaPCfi1//ZAOxNjxrvsoOP,sV/3JhFzaefl6azCgyWIoohr94Q=', u'access_token': u'MSwxNDU5OTkwODc2NTQwLDQ2NTc5MDIxMSwyOTA2LGFsbCwsLGQ1MzNkMDM2NWVkZTM1MTg5MWE1YmIxLTYyNjU4NWE2Njk2ZDNhMDUsWnhlQ1lLUUdSSkRXTGpNcW5id09fVVNCeTk0', u'expires_in': 3600, u'expires_at': 1459990870.708, u'token_type': u'bearer', 'state': 'HUXA1GPRWB9W28RV0MLDRHO8ACEUKR', u'scope': [u'all'], u'refresh_token': u'MSw0NjU3OTAyMTEsMjkwNixhbGwsZDUzM2QwMzY1ZWRlMzUxODkxYTViYjEtNjI2NTg1YTY2OTZkM2EwNSwwNjMzZDAzNjVlZGUzNTE4OTFhNWJiMS02MjY1ODVhNjY5NmQzYTA1LDE0NTk5ODcyNzQxODUseFpDUFdxQ1ZCWjFQaFNCN3hKcFBqUkJySk1n'}
	form = Mendeley_credentials_Form(token_old)
	if form.is_valid():
		form.save()
	return HttpResponse(session.token)

def credential_redirect(request):
	return HttpResponse(request.get_full_path())
