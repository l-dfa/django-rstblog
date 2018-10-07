# rstblog/views.py

import os
import pdb
import pytz
#import re
import xml.etree.ElementTree as ET
from copy import copy
from datetime      import datetime
from pathlib       import Path

from docutils.core import publish_parts
from docutils.core import publish_doctree

from markdown import markdown

from django.conf      import settings
from django.contrib   import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Exists
from django.http      import Http404
from django.http      import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import LoadArticleForm
from .models import Article
from .models import Author
from .models import Category

from .const import ARTICLES_DIR
from .const import PAGES_DIR
from .const import LANGUAGES
from .const import START_CONTENT_SIGNAL
from .const import SUFFIX
from .const import TYPES
from .const import HOME_ITEMS

# memo
#    load_article(request) #125
#    index(request)        #176
#    show(request, slug)   #161

MASTER_TYPE = list(TYPES.keys())[0]

def get_stats(atype):
    ''' statistics about indicated atype:
    
    parameters: 
        - atype            str, type of object to count (article|page)
        
    return a dictionary with these keys and values:
        - n: int        number of original articles (not a trnslation)
        - nt: int       number of translations
        - sl: set       set of used languages
        - sc: set       set of used categories
        - arg-cat1: {lng1: int, lng2: int, ...)     number of category1 articles {language1, language2, ...}
        - arg-cat2: (int, int)     number of category2 articles (original, translated,)
        - ... '''
    
    result = dict()
    n  = Article.objects.filter(translation_of__isnull=True, atype=atype).count()
    nt = Article.objects.filter(translation_of__isnull=False, atype=atype).count()
    langs = Article.objects.filter(atype=atype).values_list('language', flat=True)
    cats = Article.objects.filter(atype=atype).values_list('category__name', flat=True)
    sl = set(langs)
    sc = set(cats)
    result['n'] = n
    result['nt'] = nt
    result['sl'] = sl
    result['sc'] = sc
    for cat in sc:
        dcat = dict()
        for lng in sl:
            lc = Article.objects.filter(category__name=cat, language=lng, atype=atype).count()
            dcat[lng] = lc
        result[cat] = copy(dcat)
    #pdb.set_trace()
    return result

def show_stats(request):
    '''return statisitcs about articles in blog'''
    all_stats = dict()     # dict of dicts one every atype
    for key in list(TYPES.keys()):
        stats = get_stats(key)  # 
        all_stats[key] = stats.copy()
    data = { 'all_stats': all_stats,
             'page_id': 'rstblog:show_stats'    }
             
    return render( request, 'show_stats.html', data, )
    
    
def separate(grand_content):
    ''' return input slitted in two sections, based on the signal START_CONTENT_SIGNAL
    
    parameters:
        - gran_content          str, all the file contents as string
    
    return: a (attributes, content, ) tuple of strings
    
    note. tpical START_CONTENT_SIGNAL is '.. hic sunt leones' string '''
    
    result = None
    #pattern = f"(?P<attributes>.*)^{START_CONTENT_SIGNAL}$(?P<content>.*)"
    #m = re.search(pattern, grand_content, flags=re.M+re.S)
    #if m:
    #    result =  (m.group('attributes'), m.group('content'), )
    #return result
    ndx = grand_content.find(START_CONTENT_SIGNAL)
    if ndx != -1:
        attributes = grand_content[:ndx]
        content = grand_content[ndx+len(START_CONTENT_SIGNAL):]
        result = (attributes, content, )
    
    return result

def get_file_content(p):
    '''get file content as str
    
    parameters:
        - p         Path, of opening file
        
    return: a BYTES string
            ValueError if p isn't a file
            
    note: 
        - open file in binary mode to handle utf-8 chars
        - again: the returned value, must be decoded to obtain a unicode string '''
    
    
    content = None
    if p.is_file():
        # Note mode='rb'. Binary mode necessary to handle accented characters
        with p.open(mode='rb') as f:
            content = f.read()
    else:
        raise ValueError("File {} does not exist".format(path))
        
    return content
  
  
def upload_file(request, item_type='article', dirdst=Path(ARTICLES_DIR)):
    '''upload file to articles or pages directory
    
    parameters:
        - request     django request
        - type        str, could be article or page
        - dirdst      Path, destination directory (ARTICLES_DIR or PAGE_DIR)
    
    return: destination file as Path
            could raise exception    
            
    note: this is about upload file from client to server file system.
        creating article db record from this file is reponsability of 
    '''
    
    dst = None
    if request.method == 'POST' and request.FILES[item_type]:
        # loads file to MEDIA_ROOT using FileSystemStorage (could change filename)
        # then moves file from MEDIA_ROOT to ARTICLES_DIR (or PAGES_DIR)
        # eventually adjusting filename to the original value
        try:
            rfile = request.FILES[item_type]
            fs = FileSystemStorage()
            filename = fs.save(rfile.name, rfile)
            src = Path(settings.MEDIA_ROOT) / filename
            dst = dirdst / rfile.name
            os.replace(src, dst)
        except Exception as ex:
            raise
        finally:
            # if something was wrong and uploaded file is there yet
            # remove it
            if src.is_file():
                os.remove(src)
    else:
        raise ValueError('bad http method (must be POST) or without file to upload')
    return dst

    
def get_record(dst):
    '''get fields infos from file
    
    params:
        - dst         Path, of file to elaborate
    
    returns: a (record, autors, ) tuple, with:
        - record      dict, of file attributes
        - authors     list, of authors
        
    note.
        - get attributes and content splitting file by START_CONTENT_SIGNAL.
        - if START_CONTENT_SIGNAL there isn't, create an empty dictionary
            and populate it with default values
        - this functions may seems redundant. it isn't. after it we need
            create the Article record. Here Article.authors is a 
            m2m field: we could not load it immediatly. We need this steps:
                - create the Article
                - SAVE the article
                - add authors to article
                - save again
            during the 1st step we need the record fields value EXCEPT
            the authors. so we must split all the other fields (in record)
            from authors.
    '''
    
    file_content = get_file_content(dst)
    #pdb.set_trace()
    result = separate(file_content.decode('utf-8'))
    if result:
        attributes, content = result
        record = docinfos(attributes)
    else:
        record = dict()
    record['file'] = dst.name
    # get title
    if not record.get('title'):
        record['title'] = dst.name
    authors = []
    if record.get('authors'):
        authors.extend(copy(record.get('authors')))
    try:
        del record['authors']
    except:
        pass
    if record.get('translation_of') == '':
        del record['translation_of']
        #try:
        #    a = Author.objects.get(name=record.get('author'))
        #    authors = (a, )
        #except:
        #    pass
        #finally:
        #    del record['author']
    return (record, authors, )


#@login_required(login_url="/login/")
@login_required()
def reset_article_table(request, dir=ARTICLES_DIR):
    '''clear and rebuild article table'''
    
    all = Article.objects.all()
    hits = dict()
    for article in all:
        hits[article.title] = article.hit
    all.delete()
    paths = flatten(dir)
    #articles = [str(p.relative_to(ARTICLES_DIR)) for p in paths]
    count = 0
    for p in paths:
        article = None
        try:
            article = cOu_article_record(p, must_be_original='yes')
            if article:
                if hits.get(article.title):
                    article.hit = hits.get(article.title)
                    article.save()
                count += 1
        except Exception as ex:
            msg = 'error "{}" building record for {} article. action NOT completed'.format(ex, p.name, )
            messages.add_message(request, messages.ERROR, msg)
    for p in paths:
        article = None
        try:
            article = cOu_article_record(p, must_be_original='no')
            if article:
                if hits.get(article.title):
                    article.hit = hits.get(article.title)
                    article.save()
                count += 1
        except Exception as ex:
            msg = 'error "{}" building record for {} article. action NOT completed'.format(ex, p.name, )
            messages.add_message(request, messages.ERROR, msg)
    msg = 'loaded {} articles in DB'.format( count, )
    messages.add_message(request, messages.INFO, msg)
    return redirect('rstblog:index')

def cOu_article_record(pth, must_be_original='ignore'):
    '''create or update article record from Path
    
    parameters:
        - pth                   Path, to file to use
        - must_be_original      str, 'yes', 'no', 'ignore' (or whatever else)
                                  if 'yes' elaborate file only if original
                                  'no' elaborate only if translation
                                  'ignore' elaborate in any case
    
    return:
        - article record
        - None if ignore file
        - could raise exception '''
           
    article = None
    try:
        record, authors = get_record(pth)
        # if: must be original and is a translation
        #     OR: must be translation and is original
        #   BAIL OUT with None
        if (    (must_be_original=='yes' and 'translation_of' in record)
             or (must_be_original=='no' and not 'translation_of' in record)):
            return article
        if 'translation_of' in record and record['translation_of'] == None:
            raise ValueError(f'{pth} is translation of an unknown article')
        #  if the Article already exists, its fields are updated
        article, created = Article.objects.update_or_create(
                file=pth.name, defaults=record)
        for author in authors:
            a = Author.objects.get(name=author)
            article.authors.add(a)
        #if record.get('translation_of'):
        #    translated = Article.objects.get(title=record.get('translation_of'))
        #    article.translation_of = translated
        article.save()
    except Exception as ex:
        raise
    return article
    
#@login_required(login_url="/login/")
@login_required()
def load_article(request):
    '''load a reST|markup|html file and add/chg relative record '''
    
    article = None
    # load file to MEDIA_ROOT and move it to ARTICLES_DIR
    # then get fields from file content (docinfo section)
    # and crete/update article record in DB
    if request.method == 'POST':
        if request.FILES['article']:
            try:
                #pdb.set_trace()
                dst = upload_file(request, item_type='article', dirdst = Path(ARTICLES_DIR))
                article = cOu_article_record(dst, must_be_original='ignore')
                msg = 'article {} loaded'.format( dst.name, )
                messages.add_message(request, messages.INFO, msg)
            except Exception as ex:
                msg = 'error "{}" while trying to load article. action NOT completed'.format(ex)
                messages.add_message(request, messages.ERROR, msg)
        else:
            msg = 'file missing, nothing to upload'
            messages.add_message(request, messages.ERROR, msg)
        if article:
            return redirect('rstblog:show', slug=article.slug)
        else:
            return redirect('rstblog:index')
        
    return render( request, 'load_article.html' )


def show(request, slug=''):
    '''shows a reStructuredText file as html'''
    #pdb.set_trace()
    article = get_object_or_404(Article, published=True, slug=slug)
    
    # preaparing translations as [(language, slug), (language, slug), ...]
    trans = article.get_translations()
    translations = [(LANGUAGES.get(t.language), t.slug, t.language) for t in trans]

    # preparing article content as html
    try:
        p = ARTICLES_DIR / article.file
        infos = None
        file_content = get_file_content(p)
        result = separate(file_content.decode('utf-8'))
        if result:
            infos = docinfos(result[0])
            content = result[1][:]
        else:
            content = file_content[:]
        if ( article.markup == 'restructuredtext'
             or p.suffix == SUFFIX.reST ):
            content = rstcontent2html(content)
        elif ( article.markup == 'html'
             or p.suffix == SUFFIX.html ):
            pass
        elif ( article.markup == 'markdown'
             or p.suffix == SUFFIX.markdown ):
            content = markdown(content, extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.footnotes',])
        else:
            raise ValueError(f'{article.markup} is a markup language not supported yet')
    except:
        raise Http404()
    
    # increments article counter, if fails probably due to concurrent writes: ignoring it
    try:
        article.hit += 1
        article.save()
    except:
        pass

    data = { 'content': content, 
             'infos': infos,
             'article': article,
             'translations': translations, }
             
    return render( request, 'show.html', data, )


def index(request, category='', atype=''):
    ''' list articles '''
    
    #pdb.set_trace()
    articles = None
    ctg = None
    home = ''         # if home=='home' it is blog home flag
    if atype == '':
        home = 'home'
        atype = MASTER_TYPE
    #pdb.set_trace()
    if category=='':
        if home:
            articles = Article.objects.filter(translation_of__isnull=True, published=True, offer_home=True, atype=atype).order_by('-created')[:HOME_ITEMS]
        else:
            articles = Article.objects.filter(translation_of__isnull=True, published=True, atype=atype).order_by('-created')
    else:
        try:
            ctg = Category.objects.get(name=category)
        except Exception as ex:
            msg = f'category {category} unknown'
            messages.add_message(request, messages.ERROR, msg)
        articles = Article.objects.filter(translation_of__isnull=True, published=True, atype=atype, category=ctg.pk).order_by('-created')
            
    translations = dict()
    for article in articles:
        trans = article.get_translations()
        if len(trans) > 0:
            translations[article.title] = [(LANGUAGES.get(t.language), t.slug, ) for t in trans]
    
    #pdb.set_trace()
    data = { 'articles':     articles,
             'translations': translations,
             'category': category,
             'atype': atype,
             'page_id': f'index {category} {atype}',
             'home': home, }
    if home:
        return render( request, 'blog_home.html', data )
    else:
        return render( request, 'index.html', data )


    
def rstcontent2html(content):
    '''convert rst file content to html
    
    parameters:
        - content        str, to file to convert
        
    return: a string,
            rise ValueError if p isn't file
    '''

    extra_settings = {
        'initial_header_level': 3,
        'doctitle_xform' : 0,
        'syntax_highlight': 'short', }  # Possible values: 'long', 'short', 'none' 
    #pdb.set_trace()
    parts = publish_parts(content, writer_name='html', settings_overrides=extra_settings, )
    # in a previous version was parts['html_body']; but this includes docinfo section
    return parts['body'][:]

    
# this is from http://code.activestate.com/recipes/578948-flattening-an-arbitrarily-nested-list-in-python/
#   changing argument from list to pathlib Path directory
def flatten(path):
    '''Given a directory, possibly nested to any level, return it flattened'''
    new_lis = []
    for item in path.iterdir():
        if item.is_dir():
            new_lis.extend(flatten(item))
        else:
            new_lis.append(item)
    return new_lis

def get_field(area, field):
    result = None
    offset = len(f':{field.lower()}:')
    n0 = area.find(f':{field.lower()}:')
    if n0 != -1:
        n1 = area.find('\n', n0)
    if (n0 != -1 and n1 != -1):
        result = area[n0+offset:n1]
    elif (n0 != -1 and n1 == -1):
        result = area[n0+offset:]
    if result:
        result = result.replace('\n', ' ')
        result = result.strip()

    return result
    
def rough_docinfos(content):
    '''get docinfo fields from content
    
    params:
        - content    str, reST document
    
    return: a dict with field names as keys and field bodies as values 
    
    note: all unknown fields are discarded'''
            
    
    infos = dict()
    #field_names = []
    #field_bodies = []
    
    tree = publish_doctree(content)
    stree = str(tree)
    # INVESTIGATE. about next 4 lines: is there a better method to handle these
    #    characteristics of xml?
    stree = stree.replace('<document source="<string>">', '<document source="string">')
    stree = stree.replace('&', '&amp;')
    stree = stree.replace('["', '[&quot;')
    stree = stree.replace('"]', '&quot;]')   # to debug: load this one in text editor

    etree = ET.fromstring(stree) # line 1 col 18 errore
    
    # pdb.set_trace()
    for fname in settings.RSTBLOG.get('FIELDS'):
        if fname == 'authors':
            if 'authors' in settings.RSTBLOG.get('FIELDS'):
                authors = None
                authors = get_field(content, 'authors')
                if authors:
                    infos['authors'] = authors
        else:
            try:
                # _ are converted in - in xml class names
                cname = fname[:] if not '_' in fname else fname.replace('_', '-')
                sbody = f"./docinfo/field[@classes='{ cname }']/field_body/paragraph"
                body = etree.find(sbody).text
                body = body.replace('\n', ' ')
                body = body.strip()
                infos[fname] = body[:]
            except:
                pass
                
    return infos

    
def docinfos(content):
    '''get docinfo fields from content
    
    params:
        - content    str, reST document
    
    return: a dict with field names as keys and field bodies as values 
    
    note:
        - about field translation_of, its value may be:
            - the translated article, if found
            - None, if translated article is not found
            - in case value=='', dictionary voice is deleted'''
            
    #pdb.set_trace()
    
    infos = rough_docinfos(content)

    # elaborate category, authors, created, modified
    for name, body in infos.items():
        # elaborate created, modified
        if name in settings.RSTBLOG.get('DT_FIELDS'):
            body = norm_dt(body)
            # check https://stackoverflow.com/questions/466345/converting-string-into-datetime
            body = datetime.strptime(body, '%Y-%m-%d %H:%M:%S')
            # how use pytz? pytz.timezone(settings.TIME_ZONE)
            body = pytz.timezone(settings.TIME_ZONE).localize(body)
            infos[name] = body
        # elaborate boolean fields (published, offer home): no -> False
        if name in settings.RSTBLOG.get('BOOL_FIELDS'):
            #pdb.set_trace()
            body = body.lower()
            infos[name] = False if body == 'no' else True
        # preelaborate authors
        if name in settings.RSTBLOG.get('LIST_FIELDS'):
            #pdb.set_trace()
            body = body.split(",")
            infos[name] = body
        if name == 'authors':
            authlist = []
            for sauthor in body:
                author = None
                try:
                    author = Author.objects.get(name=sauthor)
                except:
                    continue
                if author:
                    authlist.append(author)
            infos[name] = authlist
        # check category
        if name == 'category':
            category = None
            try:
                category = Category.objects.get(name=body)
            except:
                category = Category.objects.get(name='uncategorized')
            if category:
                infos[name] = category
            else:
                del info[name]
        if name == 'translation_of':
            if body != '':
                translated = Article.objects.filter(title=body)
                if translated.exists():
                    infos[name] = translated[0]
                else:
                    infos[name] = None
            else:
                del infos[name]
        
        ## BEWARE: created and modified are date&time fields
        #if name == 'created' or name == 'modified':
        #    body = norm_dt(body)
        #    # check https://stackoverflow.com/questions/466345/converting-string-into-datetime
        #    body = datetime.strptime(body, '%Y-%m-%d %H:%M:%S')
        #    # how use pytz? pytz.timezone(settings.TIME_ZONE)
        #    #pdb.set_trace()
        #    body = pytz.timezone(settings.TIME_ZONE).localize(body)
        #if type(body) == str:
        #    body = body.replace('\n', ' ')
        #infos[name] = body
    
    return infos

    
def norm_dt(s):
    '''normalize a datetime as string
    
    params:
        - s         str, as %Y-%m-%d %H:%M:%S, maybe without %H:%M:%S

    return: string %Y-%m-%d %H:%M:%S if input has %H:%M:%S
            otherwise appends 12:00:00 to %Y-%m-%d '''
    
    ret = ''
    # yyyy-mm-dd hh:mm:ss ndx:0123-56-89 12-45-78
    if len(s) >= 10 and len(s) < 19:
        ret = s[:10] + ' 12:00:00'
    elif len(s) == 19:
        ret = s[:]
    else:
        raise ValueError('{} is not acceptable as date/time'.format(s))
    return ret
    
##### OLD GLORIES

# orginal version: read file content
def rstcontent2html_1(p):
    '''convert rst file content to html
    
    parameters:
        - p        path, to file to convert
        
    return: a string,
            rise ValueError if p isn't file
    '''
    if p.is_file():
        # Note mode='rb'. Binary mode necessary to handle accented characters
        with p.open(mode='rb') as f:
            content = f.read()
    else:
        raise ValueError("File {} does not exist".format(path))

    extra_settings = {
        'initial_header_level': 3,
        'doctitle_xform' : 0,
        'syntax_highlight': 'short', }  # Possible values: 'long', 'short', 'none' 
    #pdb.set_trace()
    parts = publish_parts(content, writer_name='html', settings_overrides=extra_settings, )
    # in a previous version was parts['html_body']; but this includes docinfo section
    return parts['body'][:]

# original version: use file name (path in arguments)
def show_1(request, path=''):
    '''shows a reStructuredText file as html'''

    p = ARTICLES_DIR / path 
    p = p.with_suffix('.rst')
    
    try:
        content = rstcontent2html(p)
    except:
        raise Http404()
    #data = { 'content': parts['html_body'],
    #         'path': path,    }
    data = { 'content': content,
             'path': path,    }
             
    return render( request, 'show.html', data, )

    
# this is the 1st version of index: file based
def index_1(request):
    ''' list articles '''
    
    paths = flatten(ARTICLES_DIR)
    articles = [str(p.relative_to(ARTICLES_DIR)) for p in paths]
    #pdb.set_trace()
    
    data = {
        'articles': articles,
    }
    return render( request, 'index.html', data )
    