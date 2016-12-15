# -*- coding: utf-8 -*-
from django.shortcuts import render
from login.models import User
from oauth2client import client
from apiclient.discovery import build
from apiclient import http, errors
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from intranet.forms import DocumentForm
from intranet.models import Document
from django.core.files import File 
import httplib2, urllib
import re, io, os, tempfile, datetime, base64, cPickle, ast, json
from django.utils.translation import ugettext as _
from django.conf import settings
flow = client.flow_from_clientsecrets(
	settings.DRIVE_JSON_DIR,
	scope='https://www.googleapis.com/auth/drive.readonly',
	redirect_uri=settings.DRIVE_REDIRECT_URI)
flow.params['include_granted_scopes'] = 'true'
flow.params['access_type'] = 'offline'

# Create your views hereself.


'''def upload_from_drive(stream, drive_id, request, thumbnail):
	owner = request.user
	try:
		meta = get_metadata(stream)
		day, month, year = date(meta['/CreationDate'])
		fields = {
			'title': meta['/Title'] if '/Title' in meta and meta['/Title']  else 'Titulo temporal' + str(datetime.datetime.now()),
			'author': meta['/Author'] if  '/Author' in meta else owner.first_name + ' ' + owner.last_name,
			'abstract': meta['/Subject'] if  '/Subject' in meta else None,
			'words': meta['/Keywords'].replace('; ', ',') if  '/Keywords' in meta else None,
			'date': year + '-' + month + '-' + day if '/CreationDate' in meta else '2000-01-01',
			'owner': owner.id,
			'drive_id': drive_id,
		}
		files = {
			'document': stream,
			'thumbnail': thumbnail,
		}
	except:
		fields = {
			'title': 'Titulo temporal' + str(datetime.datetime.now()),
			'author': owner.first_name + ' ' + owner.last_name,
			'abstract': meta['/Subject'] if  '/Subject' in meta else None,
			'words': meta['/Keywords'].replace('; ', ',') if  '/Keywords' in meta else None,
			'date': '2001-01-01',
			'owner': owner.id,
			'drive_id': drive_id,
			'type': 1,
		}
		files = {
			'document': stream  
		}
	form = DocumentForm(fields, files)
	print form.errors
	if form.is_valid():
		document = form.save()
		document.owner.update_activity().doc_number('+')
		document.format_filename()
		document.format_thumbnail_filename()
		return document.id
	else:
		return False'''



def children_list(folder_id, service, onlyPDF):
	param = {}
	param['fields'] = 'items/id'
	if onlyPDF:
		param['q'] ='mimeType="application/pdf"'
	else:
		param['q'] = 'mimeType="application/pdf" or mimeType="application/vnd.google-apps.folder"'
	children = service.children().list(folderId=folder_id, **param).execute()
	files = []
	param={}
	param['fields'] = 'fileSize,id,mimeType,ownerNames,modifiedDate,thumbnail,title'
	for child in children.get('items', []):
		# Se comprueba que el documento no exista en la bd
		document = Document.objects.filter(drive_id=child['id'])
		if not document:
			file = service.files().get(fileId=child['id'], **param).execute()
			file['ownerNames'] = file['ownerNames'][0]
			file['isFolder'] = True if file['mimeType'] == 'application/vnd.google-apps.folder' else False
			files.append(file)
	return files


# Se obtiene el servicio de Google Drive
# Si la credencial caduco, la actualiza
def get_drive_service(request):
	# Si el usuario no tiene credenciales, retorna false
	print '-------------------------', request.user.drive_credentials
	if request.user.drive_credentials == None:
		return False
	elif request.user.credentials()._expires_in() < 10:
		#Si las credenciales expiran en menos de 10 segdos (segundos?) se actualizan
		user = User.objects.get(id=request.user.id)
		credentials = request.user.credentials()
		credentials.refresh(httplib2.Http())
		#Se serializa la credencial y se almacena en la base de datos
		user.drive_credentials = base64.b64encode(cPickle.dumps(credentials))
		user.save()
	else:
		# Si las credenciales son validas, se utilizan
		credentials = request.user.credentials()
	http_auth = credentials.authorize(httplib2.Http())
	drive_service = build('drive', 'v2', http=http_auth)
	# Se retorna el servicio
	print '-------------------------',drive_service
	return drive_service


# Recibe el codigo de autorizacion de Google Drive
def oauth2callback(request):
	auth_code = request.GET['code']
	credentials = flow.step2_exchange(auth_code)
	http_auth = credentials.authorize(httplib2.Http())
	user = User.objects.get(id=request.user.id)
	user.drive_credentials = base64.b64encode(cPickle.dumps(credentials))
	request.user.drive_credentials = base64.b64encode(cPickle.dumps(credentials))
	# Se obtiene el correo de Google
	service = get_drive_service(request)
	params = get_user_data(service)
	user.drive_email = params['email']
	user.save()

	return HttpResponse('<script type="text/javascript">window.close()</script>')


# Primera llamada para obtener credenciales de Google Drive
def get_credentials(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.user.drive_credentials == None:
			auth_uri = flow.step1_get_authorize_url()
			# Retorna la url con el login de Google
			return HttpResponseRedirect(auth_uri)
		else:
			# Si el usuario ya tiene las credenciales, se cierra la ventana
			return HttpResponse('<h3> ' + _("Ya asociaste una cuenta") + '</h3> <script type="text/javascript">setTimeout(function(){window.close()}, 1000);</script>')
	else:
		# Si el usuario no inicio sesion, se le hace saber
		response = {'error': True, 'message':'Debes iniciar sesion.'}
		return JsonResponse(response)

def deauthenticate(request, redirect):
	if request.user.is_authenticated() and not request.user.is_admin:
		# Solo si el usuario posee credenciales
		if request.user.drive_credentials:
			user = User.objects.get(id=request.user.id)
			request.user.credentials().revoke(httplib2.Http())
			user.drive_credentials = None
			user.save()
		try:
			return HttpResponseRedirect(reverse(redirect, kwargs={'user_id': request.user.id}));
		except Exception as error:
			print "Error al redireccionar al usuario despues de desvincular la cuenta de Google"
			print "Excepcion: " + str(error)
			return HttpResponseRedirect(reverse('intranet:profile', kwargs={'user_id': request.user.id}))
	else:
		# Si el usuario no inicio sesion, se le redirecciona al login
		return HttpResponseRedirect(reverse('login'));

# Recibe las id de los archivos a descargar y retorna un diccionario con las id locales.
# Ids locales: Ids asignadas por la base de datos
def download_drive_files(request, ids):
	try:
		ids = ids.split('+')
		response = {'error': False}
		files = []
		local_ids=[]
		service = get_drive_service(request)
		for id in ids:
			doc, local_id = get_file_and_thumbnail(request, service, id)
			if doc is not None and local_id is not None:
				files.append(doc)
				local_ids.append(local_id)
		response['files'] = files
		response['local_ids'] = local_ids
		return JsonResponse(response)
	except errors.HttpError, error:
		return JsonResponse({'error': True, 'message':_('Hubo un problema al obtener los archivos desde Google Drive. Intentalo mas tarde.')})
	else:
		response = {'error': True, 'message':_('Debes iniciar sesion.')}
		return JsonResponse(response)

# Si no hubo problemas, retorna un diccionario con la id asignada por la base de datos
# De lo contrario retorna un mensaje de error
def get_file_and_thumbnail(request, service, id):
	file = service.files().get(fileId=id, **{'fields':'title,downloadUrl, thumbnailLink'}).execute()
	resp, content = service._http.request(file['downloadUrl'])
	if resp.status == 200:
		# Se obtiene el archivo del documento
		fh = tempfile.TemporaryFile()
		fh.write(content)
		fh.seek(0)
		document = File(fh)
		# Se obtiene el archivo de la imagen miniatura
		thumbnailLink = file['thumbnailLink'].replace('=s220', '=s600')
		file = urllib.urlopen(thumbnailLink).read()
		img = tempfile.TemporaryFile()
		img.write(file)
		img.seek(0)
		image = File(img)
		fields = {
			'owner': request.user.id,
			'drive_id': id,
			'author': request.user.first_name + ' ' + request.user.last_name,
		}
		files = {
			'document': document,
			'thumbnail': image,
		}
		form = DocumentForm(fields, files)
		print form.errors
		local_id = None
		if form.is_valid():
			document = form.save()
			doc = document.dictionary()
			local_id = document.id
			doc['error'] = False
			doc['message'] = None
		else:
			doc = {}
			doc['error'] = True
			doc['message'] = _('No se pudo descargar el documento %(title)s debibo a un problema desconocido.') % {'title': file['title']}
		return doc, local_id
	return None


# Segunda llamada. Se analizan los enlaces y se obtiene el servicio
def link_parser(request, link=None):
	if request.user.is_authenticated():
		print "---------", request.user.credentials()
		if not link:
			return JsonResponse({'error': True, 'message':'Debes anadir un enlace de Google Drive a la solicitud.'})


		# Se intenta reconocer el enlace de Google Drive
		drive_id = re.match('https:\/\/drive\.google\.com\/.*\?id=([^&]*)\&?', link)
		if not drive_id:
			drive_id = re.match('^https:\/\/drive\.google\.com\/file\/d\/(.*)\/view', link)

		if drive_id:
			drive_id = drive_id.groups()[0]
		print drive_id

		# Si no se pudo obtener la id del archivo o carpeta, se retorna el error
		if not drive_id:
			return JsonResponse({'error': True, 'message':'El link ingresado no es un enlace a Google Drive'})
			

		try:
			#request.user.credentials().revoke(httplib2.Http())

			# Se obtiene acceso al servicio de Google Drive
			service = get_drive_service(request)
			if not service:
				return JsonResponse({'error': True, 'message':_('Para continuar debes enlazar tu cuenta de Google Drive'), 'code': 'gglir'})

			param={}
			# Se definen los parametros que se quieren recibir
			param['fields'] = 'fileSize,id,modifiedDate,ownerNames,title,mimeType,owners/emailAddress,thumbnailLink,downloadUrl'
			# Se envia la solicitud
			file = service.files().get(fileId=drive_id, **param).execute()
			# Se filtra por archivos PDF o Carpeta	
			if file['mimeType'] == 'application/pdf':
				document = None
				try:
					document = Document.objects.get(drive_id=file['id'])
				except Exception as error:
					print error

				# Si el archivo ya existe, se devuelve un error
				if document:
					name  = document.title if document.title else document.drive_id
					return JsonResponse({'error': True, 'message':_('El documento <strong>' + name + '</strong> ya existe')})
				# Si excede los 2 mb, se devuelve un error
				if int(file['fileSize'])  > 2097152:
					return JsonResponse({'error': True, 'message':_('El documento no puede tener un tamano superior a 2 Megabytes.')})
				response = {
							'id': file['id'],
							'name': file['title'],
							'type': 'document',
							'date': file['modifiedDate'],
							'thumbnail': file['thumbnailLink'].replace('=s220', '=s600'),
							'size': file['fileSize'],
							'error': False,
							'credentials_expires_in': request.user.credentials()._expires_in()
							}

			elif file['mimeType'] == 'application/vnd.google-apps.folder':
				# Si es una carpeta, retorna el controlador folder_files
				return folder_files(request, file['id'])
			else:
				return JsonResponse({'error': True, 'message':_('El link ingresado no contiene documentos compatibles')})  


			#response['files'][0] = {'name':file['title'], 'size': file['fileSize'], 'content-type': file['mimeType']}

			return JsonResponse(response)   
		except errors.HttpError, error:
			print error
			try:
				get_error = re.match('(File not found)', error._get_reason()).groups()[0]
			except:
				get_error = None
			if get_error != None:
				response = {'error': True, 'message':_('No existen archivos compatibles en el enlace.')}
			else:
				response = {'error': True, 'message':_('Error desconocido. Contacta al administrador.')}           
			return JsonResponse(response)
	else:
		response = {'error': True, 'message':_('Debes iniciar sesion.')}
		return JsonResponse(response)


# Archivos del usuario #

# Formato de la respuesta de los datos del usuario
#{
# "name": "Hernán Herreros",
# "user": {
# 	"kind": "drive#user",
# 	"displayName": "Hernán Herreros",
# 	"picture": {
#  	"url": "https://lh6.googleusercontent.com/-A6PRK2NETQ8/AAAAAAAAAAI/AAAAAAAAAOw/q-j5S9v4kgg/s64/photo.jpg"
# 	},
# 	"isAuthenticatedUser": true,
# 	"permissionId": "05193559070290742252",
# 	"emailAddress": "hr.nacho.hn@gmail.com"
# },
# "rootFolderId": "0AE7EzQDMEIn7Uk9PVA"
#}
def get_user_data(service):
	param = {}
	param['fields'] = 'name,rootFolderId,user'
	about = service.about().get(**param).execute()
	param={}
	param['name'] = about['name']
	param['email'] = about['user']['emailAddress']
	param['picture'] = about['user']['picture']['url'] if 'picture' in about['user'] else None
	param['folder_id'] = about['rootFolderId'] 
	return param


def folder_files(request, folder_id = None):
	if request.user.is_authenticated():
		service = get_drive_service(request)
		print '--------------', service
		if not folder_id:
			# Si no se proporciona la id de alguna carpeta, se obtiene la informacion del usuario
			# Incluida la id de la carpeta raiz
			userData = get_user_data(service)
			folder_id = userData['folder_id']
			title = _('Raiz')
		else:
			# Se comprueba que la id corresponde a una carpeta
			param = {}
			param['fields'] = 'mimeType,title'
			file = service.files().get(fileId = folder_id, **param).execute()
			title = file['title']
			if file['mimeType'] != 'application/vnd.google-apps.folder':
				# Si la id no corresponde a una carpeta se retorna un error
				return JsonResponse({'error': True, 'message':_('Debe ingresar la ID de una carpeta')})

		# En este punto, ya tenemos la id de la carpeta
		# Se obtiene los archivos de la carpeta, solo del tipo pdf y folder
		files = children_list(folder_id, service, False)
		return JsonResponse({'error': False, 'is_folder': True, 'title': title, 'id': folder_id, 'list': sorted(files, key = lambda k: int(k['isFolder']), reverse = True)})
	else:
		return JsonResponse({'error': True, 'message':_('Debes iniciar sesion.')})