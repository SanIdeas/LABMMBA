<<<<<<< HEAD
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.mail import BadHeaderError, get_connection, EmailMultiAlternatives
from login.models import User, Area, UserManager
from intranet.models import Document
from unidecode import unidecode
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils.crypto import get_random_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt # SOLO PARA TESTING
from django.utils.translation import ugettext as _ # Para traducir un string se usa: _("String a traducir")


# Create your views here.

def home(request):
	if request.user.is_authenticated() and request.user.is_admin:
		return HttpResponseRedirect(reverse('admin:users'))
	else:
		return HttpResponseRedirect(reverse('webpage:home'))

def users(request, user_id=None, delete=False, activate=False, block=False, unblock=False, profile=False):
	if request.user.is_authenticated() and request.user.is_admin:
		if request.method == "GET":
			if activate:
				user = User.objects.get(id=user_id)
				user.is_active = True
				user.save()
				return JsonResponse({'error': False})
			elif delete:
				User.objects.get(id=user_id).delete()
				return JsonResponse({'error': False})
			elif block:
				user = User.objects.get(id=user_id)
				user.is_blocked = True
				user.save()
				return JsonResponse({'error': False})
			elif unblock:
				user = User.objects.get(id=user_id)
				user.is_blocked = False
				user.save()
				return JsonResponse({'error': False})
			elif profile:
				profile = User.objects.get(id=user_id)
				documents = Document.objects.filter(owner=user_id)
				return render(request, 'admin/profile.html', {'profile_user': profile, 'documents': documents})
			else:
				return render(request, 'admin/users.html')

		elif request.method == "POST":
			args = {
				'not_registered': User.objects.filter(is_registered=False, is_admin=False),
				'registered': User.objects.filter(is_registered=True, is_blocked=False, is_admin=False),
				'blocked': User.objects.filter(is_registered=True, is_blocked=True, is_admin=False)
			}
			return render(request, 'admin/users_ajax.html', args)

	else:
		return HttpResponseRedirect(reverse('login'))

def sendInvitation(request):
	if request.user.is_authenticated():
		if request.user.is_admin and request.method == "POST":
			error = False
			emails = request.POST["email"].split(',') # Recibe los correos electronicos separados por coma

			from_email = "LABMMBA <dev.sanideas@gmail.com>"
			subject = "[Registro] Invitación a la intranet de LABMMBA"
			text = "..."

			# Se utilizan las configuraciones SMTP de settings.py
			connection = get_connection()
			connection.open()

			# Se lee la plantilla de correos electronicos
			body = open(settings.MEDIA_ROOT + "/static/email_template/invitation_template.html", 'r')
			html = body.read().decode('UTF-8')
			body.close()

			for email in emails:
				token = ""
				while True: #Crea tokens hasta que no se repitan en la base de datos
					token = get_random_string(length=128)
					try:
						User.objects.get(access_token=token)
					except Exception:
						break
				# Crear usuario en la base de datos con su respectivo token, correo electronico y nombre
				user = User.objects.filter(email=email).first()
				if user is None or not user.is_registered:
					message = EmailMultiAlternatives(subject, text, from_email, [email])
					message.attach_alternative(html.replace('$token', token), 'text/html')

					try:
						message.send()
						if user is None:
							User.objects.precreate_user(email, token)
						else:		# Actualizar token si el usuario ya existe
							user.access_token = token
							user.save()
					except Exception:
						error = True
				else:
					error = True
			connection.close()

			if error:
				return JsonResponse({'error': True, 'message': _(u'Uno o más correos son inválidos o ya se encuentran registrados')})
			else:
				return JsonResponse({'error': False, 'message': _('')})
		elif not request.user.is_admin:
			return HttpResponseRedirect(reverse('webpage:home'))

	else:
=======
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
			return render(request, 'admin/home.html')
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

				# Se lee la plantilla de correos electronicos
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
					user = None
					try:
						user = User.objects.get(email=email)
					except Exception as error:
						print error
					if user is None:
						User.objects.precreate_user(email, token)					
						message = EmailMultiAlternatives(subject, text, from_email, [email])
						message.attach_alternative(html.replace('$token', token), 'text/html')
						message.send()
					else:
						print "El usuario " + email + " ya existe"
				connection.close()
				return JsonResponse({'error': False, 'message': _('Eres Administrador y es una solicitud POST')})
			
			else:
				return JsonResponse({'error': False, 'message':_('Eres administrador y no es una solicitud POST')})
		elif not request.user.is_admin:
			return JsonResponse({'error': True, 'message':_('Debes ser administrador.')})

	else:
>>>>>>> 0854a99110988acbeffa4c0020f0ce4c6abd5d82
		return HttpResponseRedirect(reverse('webpage:home'))