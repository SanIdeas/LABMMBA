# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.mail import BadHeaderError, get_connection, EmailMultiAlternatives
from login.models import User, Area, UserManager
from unidecode import unidecode
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils.crypto import get_random_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt # SOLO PARA TESTING
from django.utils.translation import ugettext as _ # Para traducir un string se usa: _("String a traducir")


# Create your views here.

def home(request):
	if request.user.is_authenticated():
		if request.user.is_admin:
			return HttpResponse("Eres administrador :D")
		elif not request.user.is_admin:
			return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('webpage:home'))

@csrf_exempt # SOLO PARA TESTING
def sendInvitation(request):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "POST":

				emails = request.POST["email"].split(',') # Recibe los correos electronicos separados por coma

				from_email = "LABMMBA <dev.sanideas@gmail.com>"
				subject = "[Registro] Invitación a la intranet de LABMMBA"
				text = "..."

				# Se utilizan las configuraciones SMTP de settings.py
				connection = get_connection()
				connection.open()

				body = open(settings.MEDIA_ROOT + "/static/email_template/invitation_template.html", 'r')
				html = body.read().decode('UTF-8')
				body.close()

				output = ""

				for email in emails:
					token = ""
					while True: #Crea tokens hasta que no se repitan en la base de datos
						token = get_random_string(length=128)
						try:
							User.objects.get(access_token=token)
						except Exception as error:
							output += "<h5 style='font-weight: normal'>" + email + "  -  " + token + "</h5>"
							break
					# Crear usuario en la base de datos con su respectivo token, correo electronico y nombre
					
					message = EmailMultiAlternatives(subject, text, from_email, [email])
					message.attach_alternative(html.replace('$token', token), 'text/html')
					message.send()
				connection.close()
				return JsonResponse({'error': False, 'message': _('Eres Administrador y es una solicitud POST')})
			
			else:
				return JsonResponse({'error': False, 'message':_('Eres administrador y no es una solicitud POST')})
		elif not request.user.is_admin():
			return JsonResponse({'error': True, 'message':_('Debes ser administrador.')})

	else:
		return HttpResponseRedirect(reverse('webpage:home'))