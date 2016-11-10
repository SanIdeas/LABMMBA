# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from login.models import User, Area, UserManager
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.staticfiles.templatetags.staticfiles import static
import os, datetime, base64, json, requests
from intranet.models import Document
from django.utils.translation import ugettext as _


# Create your views here.

def login(request):
	if request.method == "GET":
		if request.user.is_authenticated() == False: #Si el usuario ya esta logueado no podra ingresar a la vista Login. Se redirecciona a Intranet.
			return render(request, 'login/login.html')
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
				message = {'type': 'error', 'content': 'El administrador ha bloqueado tu cuenta.'}
				return render(request, 'login/login.html', {'message': message})
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
					message = {'type': 'error', 'content': 'Email o contraseña invalida.'}
					return render(request, 'login/login.html', {'message': message, 'email': request.POST['email']})					
			else:
				#Si el usuario no esta activo:
				message = {'type': 'error', 'content': 'Ten paciencia. Debes ser aprobado por el administrador.'}
				return render(request, 'login/login.html', {'message': message})

		else:
			#Si el usuario no existe
			message = {'type': 'error', 'content': 'Email o contraseña invalida.'}
			return render(request, 'login/login.html', {'message': message, 'email': request.POST['email']})


def logout(request):
	if request.user.is_authenticated():
		auth_logout(request)
	return HttpResponseRedirect(reverse('webpage:home'))

def register(request, token = None):
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
						return render(request, 'login/register.html', {'user': user, 'areas': Area.objects.all(), 'token': token})
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
				user  = User.objects.get(email= request.POST['email'], access_token=request.POST['access_token'])
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
						return render(request, 'login/register.html', {'user': user, 'areas': Area.objects.all()})
				else:
					# El usuario ya esta registrado, por lo tanto, se le redirecciona al login
					print "usuario ya registrado"
					return HttpResponseRedirect(reverse('login'))


			else:
				# Deberia llevar a una pagina de error: token y/o correo electronico incorrecto.
				print "token y/o correo electronico incorrecto."
				return render(request, 'login/register.html', {'user': user, 'areas': Area.objects.all()})
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
				return JsonResponse({'error': True, 'message': _(u'Hubo un problema. Asegurate de escribir correctamente tu contraseña actual.')})
		else:
			return JsonResponse({'error': True, 'message': _('Metodo de envio incorrecto')})
	else:
		return JsonResponse({'error': True, 'message': _(u'Debes iniciar sesión')})

