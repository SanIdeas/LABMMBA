# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from login.models import User, Area, UserManager
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.templatetags.staticfiles import static
import os, datetime, base64, json, requests
from intranet.models import Document


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
		user = authenticate(username=email, password=password)
		if user is not None: 
		#Si el usuario es autenticado se inicia sesion.
			auth_login(request, user)
			return HttpResponseRedirect(reverse('intranet:home'))
		else:
			message = {'type': 'error', 'content': 'Email o contraseña invalida.'}
			return render(request, 'login/login.html', {'message': message})

def signup(request):
	if request.user.is_authenticated() == False: #Si el usuario ya esta logueado no podra ingresar a la vista Login. Se redirecciona a Intranet.
			if request.method == "GET":
				return render(request, 'login/signup.html', {'areas': Area.objects.all()})
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
					message = {'type': 'error', 'content': 'El email ' + request.POST['email'] + ' ya existe.'}
					return render(request, 'login/signup.html', {'areas': Area.objects.all(), 'message': message})
	else:
		return HttpResponseRedirect(reverse('intranet:home'))


def logout(request):
	if request.user.is_authenticated() is not None:
		auth_logout(request)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER')) #Se redirecciona a la ultima pagina visitada.