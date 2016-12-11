# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.core.mail import get_connection, EmailMultiAlternatives
from login.models import User, Area, SubArea
from intranet.models import Document
from webpage.models import Section, SubSection, SubSectionCategory, News, Member, Event
from webpage.forms import SectionImageForm, ImageMemberForm
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _ # Para traducir un string se usa: _("String a traducir")
from collections import Counter
from django.conf import settings


# Create your views here.

def home(request):
	if request.user.is_authenticated() and request.user.is_admin:
		return HttpResponseRedirect(reverse('admin:users'))
	else:
		return HttpResponseRedirect(reverse('webpage:home'))


def get_filters(rqst):
	dict = {}
	for key in rqst.GET:
		if key == 'date':
			str = '__year__in'
		else:
			str = '__in'
		if len(rqst.GET.getlist(key)) > 0:
			dict[key + str] = rqst.GET.getlist(key)
	return dict


def filters_selected(list, request, name):
	count = 0
	for val in list:
		if val[0] != None:
			if unicode(val[0]) in request.GET.getlist(name):
				list[count] = val + (True,)
			elif name == 'owner' or name == 'category':
				if unicode(val[0].id) in request.GET.getlist(name):
					list[count] = val + (True,)
				else:
					list[count] = val + (False,)
					break
			else:
				list[count] = val + (False,)
		count += 1
	return list


def documents(request, search=None):
	if request.user.is_authenticated():
		if request.user.is_admin:
			kwargs = get_filters(request)
			all_docs = Document.objects.filter(**kwargs)
			if search is None: #Si no es una busqueda
				documents = all_docs
			else:
				documents = []
				high_acc_result = []
				low_acc_result = []
				authors = []
				years = []
				owners = []
				categories = []
				for document in all_docs:
					result = document.match(search)
					if result['match']:
						if result['extract'] != '':
							setattr(document, 'extract', result['extract'])
						if result['exact']:
							high_acc_result.append(document)
						else:
							low_acc_result.append(document)
						authors.append(document.author)
						years.append(document.date.year)
						owners.append(document.owner)
						categories.append(document.category)
				documents = high_acc_result + low_acc_result
				authors = filters_selected(Counter(authors).most_common(), request, 'author')
				years = filters_selected(Counter(years).most_common(), request, 'date')
				owners = filters_selected(Counter(owners).most_common(), request, 'owner')
				categories = filters_selected(Counter(categories).most_common(), request, 'category')
			parameters = {'current_view': 'admin', 'documents': documents, 'administration': Section.objects.get(slug='administrator')}
			if search is not None:
				parameters['authors'] = authors
				parameters['years'] = years
				parameters['categories'] = categories
				parameters['owners'] = owners
				parameters['search'] = search
			return render(request, 'admin/documents.html', parameters)
		else:
			return HttpResponseRedirect(reverse('webpage:home'))

	else:
		return HttpResponseRedirect(reverse('login'))


def users(request, user_id=None, delete=False, activate=False, block=False, unblock=False, profile=False):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "GET":
				if activate and request.is_ajax():
					user = User.objects.get(id=user_id)
					user.is_active = True
					user.save()
					return JsonResponse({'error': False})
				elif delete and request.is_ajax():
					User.objects.get(id=user_id).delete()
					return JsonResponse({'error': False})
				elif block and request.is_ajax():
					user = User.objects.get(id=user_id)
					user.is_blocked = True
					user.save()
					return JsonResponse({'error': False})
				elif unblock and request.is_ajax():
					user = User.objects.get(id=user_id)
					user.is_blocked = False
					user.save()
					return JsonResponse({'error': False})
				elif profile:
					profile = User.objects.get(id=user_id)
					documents = Document.objects.filter(owner=user_id)
					return render(request, 'admin/profile.html', {'profile_user': profile, 'documents': documents, 'administration': Section.objects.get(slug='administrator')})
				else:
					return render(request, 'admin/users.html', {'administration': Section.objects.get(slug='administrator')})

			elif request.method == "POST" and request.is_ajax():
				args = {
					'not_registered': User.objects.filter(is_registered=False, is_admin=False),
					'registered': User.objects.filter(is_registered=True, is_blocked=False, is_admin=False),
					'blocked': User.objects.filter(is_registered=True, is_blocked=True, is_admin=False)
				}
				return render(request, 'admin/users_ajax.html', args)
		else:
			if request.is_ajax():
				return JsonResponse({'redirect': reverse('webpage:home')})
			else:
				return HttpResponseRedirect(reverse('webpage:home'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
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
		return HttpResponseRedirect(reverse('login'))


def areas(request, area_id=None, subarea_id=None):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "GET":
				if area_id is not None and request.is_ajax():
					Area.objects.get(id=area_id).delete()
					return JsonResponse({'error': False})
				elif subarea_id is not None and request.is_ajax():
					SubArea.objects.get(id=subarea_id).delete()
					return JsonResponse({'error': False})
				else:
					return render(request, 'admin/areas.html', {'administration': Section.objects.get(slug='administrator')})

			elif request.method == "POST" and request.is_ajax():
				area_name = request.POST.get('area_name', None)
				subarea_name = request.POST.get('subarea_name', None)
				if area_name is not None:
					if area_id is not None:
						try:
							area = Area.objects.get(id=area_id)
							area.name = area_name
							area.save()
							return JsonResponse({'error': False})
						except Exception:
							return JsonResponse({'error': True, 'message': 'El área ingresada ya existe'})
					else:
						try:
							Area.objects.create(name=area_name)
							return JsonResponse({'error': False})
						except Exception:
							return JsonResponse({'error': True, 'message': 'El área ingresada ya existe'})
				elif subarea_name is not None:
					if subarea_id is not None:
						try:
							subarea = SubArea.objects.get(id=subarea_id)
							subarea.name = subarea_name
							subarea.save()
							return JsonResponse({'error': False})
						except Exception:
							return JsonResponse({'error': True, 'message': 'La subárea ingresada ya existe'})

					else:
						area_id = request.POST.get('area_id', None)
						try:
							area = Area.objects.get(id=area_id)
							try:
								area.add_sub_area(subarea_name)
								return JsonResponse({'error': False})
							except Exception:
								return JsonResponse({'error': True, 'message': 'La subárea ingresada ya existe'})
						except Exception:
							return JsonResponse({'error': True, 'message': 'El área entregada no existe'})
				else:
					areas_arr = []
					areas_obj = Area.objects.all()
					for area in areas_obj:
						areas_arr.append((area, area.get_sub_areas()))

					args = {
						'areas': areas_arr
					}

					return render(request, 'admin/areas_ajax.html', args)
		else:
			if request.is_ajax():
				return JsonResponse({'redirect': reverse('webpage:home')})
			else:
				return HttpResponseRedirect(reverse('webpage:home'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
		else:
			return HttpResponseRedirect(reverse('login'))


def webpage(request, section_id=None, subsection_id=None):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "GET":
				editable_sections = Section.objects.all().exclude(slug__in=['publications', 'intranet', 'administrator', '.', 'news'])
				return render(request, 'admin/webpage.html', {'sections': editable_sections, 'administration': Section.objects.get(slug='administrator')})

			elif request.method == "POST" and request.is_ajax():
				if section_id is not None:		# Edit section
					spanish_title = request.POST.get('spanish-title', None)
					spanish_body = request.POST.get('spanish-body', None)
					english_title = request.POST.get('english-title', None)
					english_body = request.POST.get('english-body', None)

					section = Section.objects.get(id=section_id)

					if spanish_title is not None:
						section.spanish_title = spanish_title
						section.spanish_body = spanish_body
					elif english_title is not None:
						section.english_title = english_title
						section.english_body = english_body

					try:
						section.save()
						return JsonResponse({'error': False})
					except Exception:
						return JsonResponse({'error': True})
				elif subsection_id is not None:		# Edit subsection
					spanish_title = request.POST.get('spanish-title', None)
					spanish_body = request.POST.get('spanish-body', None)
					english_title = request.POST.get('english-title', None)
					english_body = request.POST.get('english-body', None)

					subsection = SubSection.objects.get(id=subsection_id)

					if spanish_title is not None:
						subsection.spanish_title = spanish_title
						subsection.spanish_body = spanish_body
					elif english_title is not None:
						subsection.english_title = english_title
						subsection.english_body = english_body

					try:
						subsection.save()
						return JsonResponse({'error': False})
					except Exception:
						return JsonResponse({'error': True})
				else:		# Get section template data
					section_id = request.POST.get('section_id', None)
					subsection_id = request.POST.get('subsection_id', None)
					if section_id is not None:
						try:
							section = Section.objects.get(id=section_id)
							categories_arr = []
							categories_obj = section.get_categories()
							for category in categories_obj:
								categories_arr.append((category, category.get_subsections()))

							return render(request, 'admin/webpage_ajax.html', {'section': section, 'categories': categories_arr})
						except Exception:
							return JsonResponse({'error': True})
					elif subsection_id is not None:
						try:
							subsection = SubSection.objects.get(id=subsection_id)

							return render(request, 'admin/webpage_subsection_ajax.html', {'subsection': subsection})
						except Exception:
							return JsonResponse({'error': True})

		else:
			if request.is_ajax():
				return JsonResponse({'redirect': reverse('webpage:home')})
			else:
				return HttpResponseRedirect(reverse('webpage:home'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
		else:
			return HttpResponseRedirect(reverse('login'))


def upload_header(request):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "POST" and request.is_ajax():
				section_id = request.POST.get('section_id', None)
				section = Section.objects.filter(id=section_id)
				if section:
					section = section[0]
					section.update_header(request.FILES['header'])
					return JsonResponse({'error': False, 'url': section.header_static_url()})
				else:
					return JsonResponse({'error': True, 'message': u"Esta sección no existe"})

		else:
			if request.is_ajax():
				return JsonResponse({'redirect': reverse('webpage:home')})
			else:
				return HttpResponseRedirect(reverse('webpage:home'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
		else:
			return HttpResponseRedirect(reverse('login'))


def upload_thumbnail(request):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "POST" and request.is_ajax():
				category_id = request.POST.get('category_id', None)
				category = SubSectionCategory.objects.filter(id=category_id)
				if category:
					category = category[0]
					category.update_image(request.FILES['thumbnail'])
					return JsonResponse({'error': False, 'url': category.image_static_url()})
				else:
					return JsonResponse({'error': True, 'message': u"Esta sección no existe"})

		else:
			if request.is_ajax():
				return JsonResponse({'redirect': reverse('webpage:home')})
			else:
				return HttpResponseRedirect(reverse('webpage:home'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
		else:
			return HttpResponseRedirect(reverse('login'))


def save_images(request):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "POST" and request.is_ajax():
				section_id = request.POST.get('section_id', None)
				section = Section.objects.filter(id=section_id)
				if section:
					response = {}
					for key in request.FILES:
						fields = {
							'section': section_id
						}
						files = {
							'image': request.FILES[key]
						}
						form = SectionImageForm(fields, files)
						if form.is_valid():
							image = form.save()
							image.set_filename()
							response[key] = image.static_url()
						else:
							return JsonResponse({'error': True, 'message': form.errors})

					return JsonResponse({'error': False, 'urls': response})
				else:
					return JsonResponse({'error': True, 'message': u"Esta sección no existe"})

		else:
			if request.is_ajax():
				return JsonResponse({'redirect': reverse('webpage:home')})
			else:
				return HttpResponseRedirect(reverse('webpage:home'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
		else:
			return HttpResponseRedirect(reverse('login'))


def members(request, member_id=None, work=False, unwork=False):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "GET":
				if work and request.is_ajax():
					member = Member.objects.get(id=member_id)
					member.working = True
					member.save()
					return JsonResponse({'error': False})
				elif unwork and request.is_ajax():
					member = Member.objects.get(id=member_id)
					member.working = False
					member.save()
					return JsonResponse({'error': False})
				elif member_id is not None and request.is_ajax():
					Member.objects.get(id=member_id).delete()
					return JsonResponse({'error': False})
				
				else:
					return render(request, 'admin/members.html', {'administration': Section.objects.get(slug='administrator')})

			elif request.method == "POST" and request.is_ajax():
				member_name = request.POST.get('member_name', None)
				member_description = request.POST.get('member_description', None)
				if member_name is not None:
					if member_id is not None:
						try:
							member = Member.objects.get(id=member_id)
							member.description = member_description
							member.save()
							return JsonResponse({'error': False})
						except Exception:
							return JsonResponse({'error': True, 'message': 'El integrante ingresado ya existe'})
					else:
						try:
							Member.objects.create(name=member_name)
							return JsonResponse({'error': False})
						except Exception:
							return JsonResponse({'error': True, 'message': 'El integrante ingresado ya existe'})
				else:
					members_arr = []
					members_obj = Member.objects.all()
		
					for member in members_obj:
						members_arr.append((member))

					args = {
						'working': Member.objects.filter(working=True),
						'not_working': Member.objects.filter(working=False),
					}

					return render(request, 'admin/members_ajax.html', args)
		else:
			if request.is_ajax():
				return JsonResponse({'redirect': reverse('webpage:home')})
			else:
				return HttpResponseRedirect(reverse('webpage:home'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
		else:
			return HttpResponseRedirect(reverse('login'))


def update_member_picture(request):
	if request.user.is_authenticated() and request.user.is_admin:
		member = request.POST.get('member', None);
		Member.objects.get(id=member).update_picture(request.FILES['picture'])
		Member.objects.get(id=member).set_image_filename();
		return JsonResponse({'error': False})


def news(request, news_id=None, publish=False, unpublish=False, show_header=False, hide_header=False):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "GET":
				if publish and request.is_ajax():
					news_obj = News.objects.get(id=news_id)
					if not news_obj.title:
						return JsonResponse({'error': True, 'message': 'No se puede aprobar una noticia sin título'})

					news_obj.is_published = True
					news_obj.save()
					return JsonResponse({'error': False})
				elif unpublish and request.is_ajax():
					news_obj = News.objects.get(id=news_id)
					news_obj.is_published = False
					news_obj.in_header = False
					news_obj.save()
					return JsonResponse({'error': False})
				elif show_header and request.is_ajax():
					news_obj = News.objects.get(id=news_id)
					if not news_obj.title:
						return JsonResponse({'error': True, 'message': 'No se puede poner en la cabecera una noticia sin título'})
					elif not news_obj.is_published:
						return JsonResponse({'error': True, 'message': 'No se puede poner en la cabecera una noticia no publicada'})

					news_obj.in_header = True
					news_obj.save()
					return JsonResponse({'error': False})
				elif hide_header and request.is_ajax():
					news_obj = News.objects.get(id=news_id)
					news_obj.in_header = False
					news_obj.save()
					return JsonResponse({'error': False})
				else:
					return render(request, 'admin/news.html', {'administration': Section.objects.get(slug='administrator')})

			elif request.method == "POST" and request.is_ajax():
				args = {
					'not_published': News.objects.filter(is_published=False).order_by('-date'),
					'published': News.objects.filter(is_published=True).order_by('-date'),
					'news_in_header': News.objects.filter(is_published=True, in_header=True).count()
				}
				return render(request, 'admin/news_ajax.html', args)
		else:
			if request.is_ajax():
				return JsonResponse({'redirect': reverse('webpage:home')})
			else:
				return HttpResponseRedirect(reverse('webpage:home'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
		else:
			return HttpResponseRedirect(reverse('login'))


def events(request, event_id=None):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "GET":
				if event_id is not None and request.is_ajax():
					Event.objects.get(id=event_id).delete()
					return JsonResponse({'error': False})
				else:
					return render(request, 'admin/events.html', {'administration': Section.objects.get(slug='administrator')})

			elif request.method == "POST" and request.is_ajax():
				args = {
					'events': sorted(Event.objects.all(), key=lambda event: event.get_date(), reverse=True)
				}
				return render(request, 'admin/events_ajax.html', args)
		else:
			if request.is_ajax():
				return JsonResponse({'redirect': reverse('webpage:home')})
			else:
				return HttpResponseRedirect(reverse('webpage:home'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
		else:
			return HttpResponseRedirect(reverse('login'))


def event_create(request):
	if request.user.is_authenticated():
		if request.user.is_admin:
			if request.method == "GET":
				return render(request, 'admin/event_create.html', {'administration': Section.objects.get(slug='administrator')})
		else:
			if request.is_ajax():
				return JsonResponse({'redirect': reverse('webpage:home')})
			else:
				return HttpResponseRedirect(reverse('webpage:home'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
		else:
			return HttpResponseRedirect(reverse('login'))