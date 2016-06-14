from django.shortcuts import render
from django.http import JsonResponse
from login.models import User
from oauth2client import client
from apiclient.discovery import build
from apiclient import http, errors
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files import File 
from intranet.views import get_metadata, strip_accents, convert_pdf_to_txt
from intranet.forms import DocumentForm
from intranet.models import Document
from PIL import Image
import httplib2, urllib, cStringIO
import re, io, os, tempfile, datetime, base64, cPickle, ast, json
from django.utils.translation import ugettext as _
flow = client.flow_from_clientsecrets(
    'drive/client_secret.json',
    scope='https://www.googleapis.com/auth/drive.readonly',
    redirect_uri='http://nachoherrs.ddns.net/drive/oauth2callback')
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
        print meta
        day, month, year = date(meta['/CreationDate'])
        fields = {
            'title': meta['/Title'] if '/Title' in meta else 'Titulo temporal' + str(datetime.datetime.now()),
            'author': meta['/Author'] if  '/Author' in meta else owner.first_name + ' ' + owner.last_name,
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
        try:
            text_file = open(document.document.url.replace('pdf', 'txt'), 'w')
            text_from_file = strip_accents(convert_pdf_to_txt(document.document.url))
            text_file.write(text_from_file.lower())
            text_file.close()
        except:
            text_file = open(document.document.url.replace('pdf', 'txt'), 'w')
            text_file.close()
        document.save_abstract()
        document.keywords()
        return document.id
    else:
        return False



def children_list(folder_id, service):
    param = {}
    param['q'] ='mimeType="application/pdf"'
    children = service.children().list(folderId=folder_id, **param).execute()
    files = []
    param={}
    param['fields'] = 'fileSize,id,modifiedDate,ownerNames,title'
    for child in children.get('items', []):
        file = service.files().get(fileId=child['id'], **param).execute()
        file['ownerNames'] = file['ownerNames'][0]
        files.append(file)
    return files



def get_drive_service(request):
    print request.user.credentials()
    if request.user.drive_credentials == None:
        return False
    elif request.user.credentials()._expires_in() < 10:
        user = User.objects.get(id=request.user.id)
        credentials = request.user.credentials()
        credentials.refresh(httplib2.Http())
        user.drive_credentials = base64.b64encode(cPickle.dumps(credentials))
        user.save()
    else:
        credentials = request.user.credentials()
    http_auth = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v2', http=http_auth)
    return drive_service


def oauth2callback(request):
    auth_code = request.GET['code']
    credentials = flow.step2_exchange(auth_code)
    http_auth = credentials.authorize(httplib2.Http())
    user = User.objects.get(id=request.user.id)
    user.drive_credentials = base64.b64encode(cPickle.dumps(credentials))
    user.save()
    return HttpResponse('<script type="text/javascript">window.close()</script>')

def get_credentials(request):
    if request.user.is_authenticated():
        if request.user.drive_credentials == None:
            auth_uri = flow.step1_get_authorize_url()
            return HttpResponseRedirect(auth_uri)
        else:
            return HttpResponseRedirect(reverse('link_analizer', args={''}))
    else:
        response = {'error': True, 'message':'Debes iniciar sesion.'}
        return JsonResponse(response)



def link_analizer(request, link=None):
    if request.user.is_authenticated():
        if not link:
            return JsonResponse({'error': True, 'message':'Debes anadir un enlace de Google Drive a la solicitud.'})

        try:
            drive_id = re.match('https:\/\/drive\.google\.com\/.*\?id=([^&]*)\&?', link).groups()[0]
        except:
            try:
                drive_id = re.match('^https:\/\/drive\.google\.com\/file\/d\/(.*)\/view', link).groups()[0]
            except:
                return JsonResponse({'error': True, 'message':'El link ingresado no es un enlace a Google Drive'})
            

        try:
            #request.user.credentials().revoke(httplib2.Http())
            service = get_drive_service(request)
            if not service:
                return JsonResponse({'error': True, 'message':_('Para continuar debes enlazar tu cuenta de Google Drive'), 'code': 'gglir'})
            param={}
            param['fields'] = 'fileSize,id,modifiedDate,ownerNames,title,mimeType,owners/emailAddress,thumbnailLink,downloadUrl'
            file = service.files().get(fileId=drive_id, **param).execute()
            if file['mimeType'] == 'application/pdf':
                file['ownerNames'] = file['ownerNames'][0]
                response = {'file': file, 'type': 'PDF Document', 'link': link, 'error': False, 'credentials_expires_in': request.user.credentials()._expires_in()}

            elif file['mimeType'] == 'application/vnd.google-apps.folder':
                response = {'files': children_list(drive_id, service), 'folder_name': file['title'], 'type': 'Folder', 'link': link, 'error': False, 'credentials_expires_in': request.user.credentials()._expires_in()}
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
        service = get_drive_service(request)
        for id in ids:
            file = service.files().get(fileId=id, **{'fields':'title,downloadUrl, thumbnailLink'}).execute()
            resp, content = service._http.request(file['downloadUrl'])
            if resp.status == 200:
                fh = tempfile.TemporaryFile()
                fh.write(content)
                fh.seek(0)
                thumbnailLink = file['thumbnailLink']
                file = urllib.urlopen(thumbnailLink).read()
                img = tempfile.TemporaryFile()
                img.write(file)
                img.seek(0)
                local_id = upload_from_drive(File(fh), id, request, File(img))
                doc = Document.objects.get(id=local_id).dictionary()
                doc['error'] = False
                doc['message'] = None
                files.append(doc)
            else:
                files.append({'error': True, 'message': _('No se pudo descargar el documento %(title)s debibo a un problema desconocido.') % {'title': file['Title']}})
        response['files'] = files
        return JsonResponse(response)
    except errors.HttpError, error:
        return JsonResponse({'error': True, 'message':_('Hubo un problema al obtener los archivos desde Google Drive. Intentalo mas tarde.')})
    else:
        response = {'error': True, 'message':_('Debes iniciar sesion.')}
        return JsonResponse(response)