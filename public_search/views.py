# -*- coding: utf-8 -*-
from django.shortcuts import render
from intranet.models import Document
from unidecode import unidecode
from django.http import HttpResponseRedirect
from webpage.models import Section
from login.models import SubArea, Area, User
from django.core.urlresolvers import reverse
from intranet.views import get_filters, filters_selected
from collections import Counter
from django.core.paginator import Paginator

# Create your views here.
def search(request, search=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('intranet'))
    else:
        kwargs = get_filters(request)
        sections = Section.objects.all()
        section = Section.objects.get(slug='publications')
        parameters = {
            'current_view': section, 'current_section': section,
            'other_sections': sections.exclude(slug__in=['.', 'publications', 'intranet', 'administrator', section.slug])[:3],
            'sections': sections.exclude(slug__in=['intranet', 'administrator']),
            'body': 'eventos'
            }

        try:
            all_docs = Document.objects.filter(is_available=True, is_public=True, **kwargs).exclude(title__isnull=True, author__isnull=True)
        except:
            all_docs = Document.objects.filter(is_available=True, is_public=True).exclude(title__isnull=True, author__isnull=True)


        #Si no es una busqueda
        if search is None:
            paginator = Paginator(all_docs, 10);
            # Se obtienen las categorias disponibles
            parameters['categories'] = []
            for category in Document.objects.filter(is_available=True, is_public=True).values('category').distinct():
                parameters['categories'].append(SubArea.objects.get(id=category['category']))

            # Se extrae el numero de pagina
            if request.GET.get('page'):
                try: parameters['documents'] = paginator.page(request.GET.get('page'))
                except: parameters['documents'] = paginator.page(1)
            else:
                parameters['documents'] = paginator.page(1)

        # Si es una busqueda
        else:
            documents = []
            high_acc_result = [] # Resultados de alta presicion
            low_acc_result = [] # Resultados de baja presicion

            # Lista con los authores, años, dueños y categorias, y sus contadores.
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

            # Se obtiene los datos del filtro
            documents = high_acc_result + low_acc_result
            authors = filters_selected(Counter(authors).most_common(), request, 'author')
            years = filters_selected(Counter(years).most_common(), request, 'date')
            owners = filters_selected(Counter(owners).most_common(), request, 'owner')
            categories = filters_selected(Counter(categories).most_common(), request, 'category')

            # Se almacenan los documentos en los parametros
            parameters['documents'] = documents

            parameters['authors'] = authors
            parameters['years'] = years
            parameters['categories'] = categories
            print categories
            parameters['owners'] = owners
            parameters['search'] = search
            


        return render(request, 'public_search/search.html', parameters)