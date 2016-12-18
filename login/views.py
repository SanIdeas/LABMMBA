# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from login.models import User, Area, UserManager
from webpage.models import Section
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.staticfiles.templatetags.staticfiles import static
import os, datetime, base64, json, requests
from intranet.models import Document
from django_countries import countries
from django.utils.translation import ugettext as _
from django.core.mail import get_connection, EmailMultiAlternatives
from django.conf import settings
from django.utils.crypto import get_random_string

# Create your views here.

def login(request):
	if request.user.is_authenticated():
		if request.user.is_admin:
			exclude = ['intranet', 'publications']
		else:
			exclude = ['administrator', 'publications']
	else:
		exclude = ['intranet', 'administrator']

	section = Section()
	section.spanish_name = 'Ingresar'
	section.english_name = 'Login'
	section.slug = 'login'

	sections = Section.objects.all()

	if request.method == "GET":
		if request.user.is_authenticated() == False: #Si el usuario ya esta logueado no podra ingresar a la vista Login. Se redirecciona a Intranet.
			return render(request, 'login/login.html', {
				'current_view': section,
				'current_section': section,
				'sections': sections.exclude(slug__in=exclude)
			})
		else:
			return HttpResponseRedirect(reverse('intranet:home')) #Se redirecciona a la ultima pagina visitada.			
	else:
		email = request.POST['email']
		password = request.POST['password']
		try:
			user = User.objects.get(email=email)
		except:
			user = None
		print user
		if user is not None:
			if user.is_blocked:
				message = {'type': 'error', 'content': _(u'El administrador ha bloqueado tu cuenta.')}
				return render(request, 'login/login.html', {'message': message, 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})
			elif user.is_active:
				user_ = authenticate(username=email, password=password)
				if user_ is not None:
					#Si el usuario es autenticado se inicia sesion.
					auth_login(request, user_)
					if user.is_admin:
						return HttpResponseRedirect(reverse('admin:home'))
					else:
						return HttpResponseRedirect(reverse('intranet:home'))
				else:
					#Si el usuario no fue autenticado, se envia un mensaje de error
					message = {'type': 'error', 'content': _(u'Email o contraseña inválida.')}
					return render(request, 'login/login.html', {'message': message, 'email': request.POST['email'], 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})
			else:
				#Si el usuario no esta activo:
				message = {'type': 'error', 'content': _(u'Ten paciencia. Debes ser aprobado por el administrador.')}
				return render(request, 'login/login.html', {'message': message, 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})

		else:
			#Si el usuario no existe
			message = {'type': 'error', 'content': _(u'Email o contraseña inválida.')}
			return render(request, 'login/login.html', {'message': message, 'email': request.POST['email'], 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})


def logout(request):
	if request.user.is_authenticated():
		auth_logout(request)
	return HttpResponseRedirect(reverse('webpage:home'))


def register(request, token = None):
	if request.user.is_authenticated():
		if request.user.is_admin:
			exclude = ['intranet', 'publications']
		else:
			exclude = ['administrator', 'publications']
	else:
		exclude = ['intranet', 'administrator']

	section = Section()
	section.spanish_name = 'Registro'
	section.english_name = 'Register'
	section.slug = 'login/register/'

	sections = Section.objects.all()

	if token:
		section.slug += token

	if token == "":
		token = None
	if not request.user.is_authenticated():
		if request.method == "GET":
			if token is not None:
				user = None
				try:
					user  = User.objects.get(access_token=token)
				except Exception as error:
					print error
					
				if user is not None:
					if user.is_registered:
						#Aqui deberia decirle al usuario que este usuario ya esta registrado
						print "usuario ya registrado"
						return HttpResponseRedirect(reverse('webpage:home'))
					else:
						return render(request, 'login/register.html', {'user': user, 'areas': Area.objects.all(), 'token': token, 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude), 'countries': list(countries)})
				else:
					#Aqui deberia decirle al usuario que el token no es valido
					return HttpResponseRedirect(reverse('webpage:home'))
			else:
				# Aqui deberia decirle al usuario que el token de registro no existe o algo por el estilo
				return HttpResponseRedirect(reverse('webpage:home'))
		elif request.method == "POST":
			# 
			user = None
			try:
				user = User.objects.get(email= request.POST['email'], access_token=request.POST['access_token'])
			except Exception as error:
				print "Error: " + str(error)

			if user is not None:
				if not user.is_registered:
					registration = user.complete_registration(
						request.POST['first_name'],
						request.POST['last_name'],
						request.POST['institution'],
						request.POST['country'],
						request.POST['area'],
						request.POST['career'],
						request.POST['password'])
					if registration:
						# Registro exitoso. Se inicia sesion
						user_ = authenticate(username=request.POST['email'], password=request.POST['password'])
						#Si el usuario es autenticado se inicia sesion.
						auth_login(request, user_)
						print "registro exitoso"
						return HttpResponseRedirect(reverse('intranet:home'))
					else:
						# Falto un campo
						print "falta un campo"
						return render(request, 'login/register.html', {'user': user, 'areas': Area.objects.all(), 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})
				else:
					# El usuario ya esta registrado, por lo tanto, se le redirecciona al login
					print "usuario ya registrado"
					return HttpResponseRedirect(reverse('login'))


			else:
				# Deberia llevar a una pagina de error: token y/o correo electronico incorrecto.
				print "token y/o correo electronico incorrecto."
				return render(request, 'login/register.html', {'user': user, 'areas': Area.objects.all(), 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})
		else:
			# si no es GET o POST, se redirecciona a la pagina de inicio
			return HttpResponseRedirect(reverse('webpage:home'))

	else:
		return HttpResponseRedirect(reverse('webpage:home'))


def change_password(request):
	if request.user.is_authenticated():
		if request.method == "POST":
			new = request.POST['new']
			current = request.POST['current']

			# Se comprueba que la contraseña actual coincida
			authenticate_ = authenticate(username=request.user.email, password=current)

			if authenticate_:
				request.user.set_password(new)
				request.user.save()
				# Se obtiene la nueva sesion
				authenticate_ = authenticate(username=request.user.email, password=new)
				auth_login(request, authenticate_)
				return JsonResponse({'error': False, 'message': _('Cambio exitoso')})
			else:
				return JsonResponse({'error': True, 'message': _(u'Hubo un problema. Asegúrate de escribir correctamente tu contraseña actual.')})
		else:
			return JsonResponse({'error': True, 'message': _(u'Metodo de envío incorrecto')})
	else:
		return JsonResponse({'error': True, 'message': _(u'Debes iniciar sesión')})

def recover_password(request):
	if not request.user.is_authenticated():
		exclude = ['intranet', 'administrator']

		section = Section()
		section.spanish_name = 'Ingresar'
		section.english_name = 'Login'
		section.slug = 'login'

		sections = Section.objects.all()
		if request.method == "GET":
			return render(request, 'login/email.html', {'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})
		else:
			print request.POST.get('email')
			user = User.objects.filter(email=request.POST.get('email'))
			if user:
				user = user[0]
				if not send_email(user):
					message = {'type': 'success', 'content': _(u'Enviado con éxito. Revisa tu bandeja de entrada')}
					return render(request, 'login/email.html', {'message': message,'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})
				else:
					message = {'type': 'error', 'content': _(u'Hubo un error inesperado. Inténtalo más tarde.')}
					return render(request, 'login/email.html', {'email': request.POST.get('email'), 'message': message, 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})	
			else:
				message = {'type': 'error', 'content': _(u'El correo electrónico no es válido')}
				return render(request, 'login/email.html', {'email': request.POST.get('email'), 'message': message, 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})
	else:
		return HttpResponseRedirect(reverse('webpage:home'))

def recover_password_callback(request, token=None):
	if not request.user.is_authenticated():
		exclude = ['intranet', 'administrator']

		section = Section()
		section.spanish_name = 'Ingresar'
		section.english_name = 'Login'
		section.slug = 'login'

		sections = Section.objects.all()

		if request.method == "GET":
			if not token:
				return HttpResponseRedirect(reverse('recover_password'))
			user = User.objects.filter(recovery_token=token)
			if user:
				return render(request, 'login/recovery.html', {'token': token, 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})
			else:
				return HttpResponseRedirect(reverse('recover_password'))
		else:
			if request.POST.get('recovery_token') is not None:
				user = User.objects.filter(recovery_token=request.POST.get('recovery_token'))
				print '---  ', user
				if user:
					user = user[0]
					user.set_password(request.POST.get('password'))
					user.recovery_token = None
					user.save()
					return HttpResponseRedirect(reverse('login'))
			
			message = {'type': 'error', 'content': _(u'Token no valido')}
			return render(request, 'login/recovery.html', {'token': token, 'message': message, 'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=exclude)})
	else:
		return HttpResponseRedirect(reverse('webpage:home'))

# Retorna False si no hay errores
def send_email(user):
	error = False

	from_email = "LABMMBA <dev.sanideas@gmail.com>"
	subject = "[Contraseña] Recuperación de contraseña"
	text = "..."

	# Se utilizan las configuraciones SMTP de settings.py
	connection = get_connection()
	connection.open()

	# Se lee la plantilla de correos electronicos
	body = open(settings.MEDIA_ROOT + "/static/email_template/recovery_template.html", 'r')
	html = body.read().decode('UTF-8')
	body.close()
	token = ""
	while True: #Crea tokens hasta que no se repitan en la base de datos
		token = get_random_string(length=128)
		try:
			User.objects.get(access_token=token)
		except Exception:
			break

	message = EmailMultiAlternatives(subject, text, from_email, [user.email])
	message.attach_alternative(html.replace('$token', token).replace('$user', user.first_name + ' ' + user.last_name).replace('$redirect', settings.EMAIL_REDIRECT_URL).replace('$header', settings.EMAIL_HEADER_URL).replace('$footer', settings.EMAIL_FOOTER_URL), 'text/html')

	try:
		message.send()		
		# Actualiza el token de recuperacion
		user.recovery_token = token
		user.save()
	except Exception:
		error = True
	connection.close()
	return error