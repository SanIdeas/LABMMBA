# -*- coding: utf-8 -*-
from django.shortcuts import render
from login.models import User
from oauth2client import client
from apiclient.discovery import build
from apiclient import http, errors
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.core.files import File 
from intranet.views import get_metadata, strip_accents, convert_pdf_to_txt
from intranet.forms import DocumentForm
from intranet.models import Document
import httplib2, urllib, cStringIO
import re, io, os, tempfile, datetime, base64, cPickle, ast, json
from django.utils.translation import ugettext as _
from django.conf import settings
flow = client.flow_from_clientsecrets(
	settings.DRIVE_JSON_DIR,
	scope='https://www.googleapis.com/auth/drive.readonly',
	redirect_uri='http://127.0.0.1:8000/drive/oauth2callback')
flow.params['include_granted_scopes'] = 'true'
flow.params['access_type'] = 'offline'

# Create your views hereself.

def date(date):
	if date[0] == 'D':
		year = date[2:6]
		month = date[6:8]
		day = date[8:10]
		return day, month, year
	else:
		month, day, year = re.match('([0-9])*\/([0-9]*)\/([0-9]*)', date).groups()
		return day, month, year

def upload_from_drive(stream, drive_id, request, thumbnail):
	owner = request.user
	try:
		meta = get_metadata(stream)
		day, month, year = date(meta['/CreationDate'])
		fields = {
			'title': meta['/Title'] if '/Title' in meta else 'Titulo temporal' + str(datetime.datetime.now()),
			'author': meta['/Author'] if  '/Author' in meta else owner.first_name + ' ' + owner.last_name,
			'abstract': meta['/Subject'] if  '/Subject' in meta else None,
			'words': meta['/Keywords'].replace('; ', ',') if  '/Keywords' in meta else None,
			'date': year + '-' + month + '-' + day if '/CreationDate' in meta else '2000-01-01',
			'owner': owner.id,
			'drive_id': drive_id,
			'type': 1,
			'drive_thumbnail': thumbnail if thumbnail else None,
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
			'drive_thumbnail': thumbnail if thumbnail else None,
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
		#try:
		#    text_file = open(document.document.url.replace('pdf', 'txt'), 'w')
		#    text_from_file = strip_accents(convert_pdf_to_txt(document.document.url))
		#    text_file.write(text_from_file.lower())
		#    text_file.close()
		#except:
		#    text_file = open(document.document.url.replace('pdf', 'txt'), 'w')
		#    text_file.close()
		#document.save_abstract()
		#document.keywords()
		return document.id
	else:
		return False



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
		file = service.files().get(fileId=child['id'], **param).execute()
		file['ownerNames'] = file['ownerNames'][0]
		file['isFolder'] = True if file['mimeType'] == 'application/vnd.google-apps.folder' else False
		files.append(file)
	return files


# Se obtiene el servicio de Google Drive
# Si la credencial caduco, la actualiza
def get_drive_service(request):
	# Si el usuario no tiene credenciales, retorna false
	if request.user.drive_credentials == None:
		return False
	elif request.user.credentials()._expires_in() < 10:
		#Si las credenciales expiran en menos de 10 segundos (segundos?) se actualizan
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
	return drive_service


# Recibe el codigo de autorizacion de Google Drive
def oauth2callback(request):
	auth_code = request.GET['code']
	credentials = flow.step2_exchange(auth_code)
	http_auth = credentials.authorize(httplib2.Http())
	user = User.objects.get(id=request.user.id)
	user.drive_credentials = base64.b64encode(cPickle.dumps(credentials))
	user.save()
	return HttpResponse('<script type="text/javascript">window.close()</script>')


# Primera llamada para obtener credenciales de Google Drive
def get_credentials(request):
	print request.user.is_authenticated()
	if request.user.is_authenticated():
		if request.user.drive_credentials == None:
			auth_uri = flow.step1_get_authorize_url()
			# Retorna la url con el login de Google
			return HttpResponseRedirect(auth_uri)
		else:
			# Si el usuario ya tiene las credenciales, es redireccinado al analizador de enlaces
			# Revisar esto. Esta raro
			return HttpResponseRedirect(reverse('link_analizer', args={''}))
	else:
		# Si el usuario no inicio sesion, se le hace saber
		response = {'error': True, 'message':'Debes iniciar sesion.'}
		return JsonResponse(response)


# Segunda llamada. Se analizan los enlaces y se obtiene el servicio
def link_analizer(request, link=None):
	if request.user.is_authenticated():
		print "---------", request.user.credentials()
		if not link:
			return JsonResponse({'error': True, 'message':'Debes anadir un enlace de Google Drive a la solicitud.'})

		# Se intenta reconocer el enlace de Google Drive
		try:
			drive_id = re.match('https:\/\/drive\.google\.com\/.*\?id=([^&]*)\&?', link).groups()[0]
		except:
			try:
				drive_id = re.match('^https:\/\/drive\.google\.com\/file\/d\/(.*)\/view', link).groups()[0]
			except:
				return JsonResponse({'error': True, 'message':'El link ingresado no es un enlace a Google Drive'})
			

		try:
			#request.user.credentials().revoke(httplib2.Http())
			# Se obtiene acceso al servicio de Google Drive
			
			print "---------", request.user.drive_credentials
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
				file['ownerNames'] = file['ownerNames'][0]
				response = {'file': file, 'type': 'PDF Document', 'link': link, 'error': False, 'credentials_expires_in': request.user.credentials()._expires_in()}

			elif file['mimeType'] == 'application/vnd.google-apps.folder':
				# Si es una carpeta, se llama a la funcion children_list
				response = {'files': children_list(drive_id, service, True), 'folder_name': file['title'], 'type': 'Folder', 'link': link, 'error': False, 'credentials_expires_in': request.user.credentials()._expires_in()}
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

#Recibe las id de los archivos a descargar y retorna un diccionario con las id locales.
def download_drive_files(request, ids):
	try:
		ids = ids.split('+')
		response = {'error': False}
		files = []
		real_ids=[]
		service = get_drive_service(request)
		for id in ids:
			file = service.files().get(fileId=id, **{'fields':'title,downloadUrl, thumbnailLink'}).execute()
			resp, content = service._http.request(file['downloadUrl'])
			if resp.status == 200:
				fh = tempfile.TemporaryFile()
				fh.write(content)
				fh.seek(0)
				thumbnailLink = file['thumbnailLink'].replace('=s220', '=s320')
				file = urllib.urlopen(thumbnailLink).read()
				img = tempfile.TemporaryFile()
				img.write(file)
				img.seek(0)
				local_id = upload_from_drive(File(fh), id, request, File(img))
				real_ids.append(local_id)
				doc = Document.objects.get(id=local_id).dictionary()
				doc['error'] = False
				doc['message'] = None
				files.append(doc)
			else:
				files.append({'error': True, 'message': _('No se pudo descargar el documento %(title)s debibo a un problema desconocido.') % {'title': file['Title']}})
		response['files'] = files
		response['real_ids'] = real_ids
		return JsonResponse(response)
	except errors.HttpError, error:
		return JsonResponse({'error': True, 'message':_('Hubo un problema al obtener los archivos desde Google Drive. Intentalo mas tarde.')})
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
	param['picture'] = about['user']['picture']['url'] if 'picture' in about['user'] else None
	param['folderId'] = about['rootFolderId'] 
	return param


def user_files(request, folderId = None):
	if request.user.is_authenticated():
		service = get_drive_service(request)
		if not folderId:
			# Si no se proporciona la id de alguna carpeta, se obtiene la informacion del usuario
			# Incluida la id de la carpeta raiz
			userData = get_user_data(service)
			folderId = userData['folderId']
		else:
			# Se comprueba que la id corresponde a una carpeta
			param = {}
			param['fields'] = 'mimeType'
			file = service.files().get(fileId = folderId, **param).execute()
			if file['mimeType'] != 'application/vnd.google-apps.folder':
				# Si la id no corresponde a una carpeta se retorna un error
				return JsonResponse({'error': True, 'message':_('Debe ingresar la ID de una carpeta')})

		# En este punto, ya tenemos la id de la carpeta
		# Se obtiene los archivos de la carpeta, solo del tipo pdf y folder
		files = children_list(folderId, service, False)
		return JsonResponse({'error': False, 'list': sorted(files, key = lambda k: int(k['isFolder']), reverse = True)})
	else:
		return JsonResponse({'error': True, 'message':_('Debes iniciar sesion.')})