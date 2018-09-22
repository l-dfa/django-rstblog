# rstblog/tests.py

# MEMO #ppp func(self)

_ENV = '''tests environment
   
   contents directory::
   
   .../testcontents/
          |-- articles/
          |      |-- article.rts
          |      +-- article.en.rts
          |-- media/
          +-- pages/
          
'''

# WARNING

# DO NOT test for exception with other tests in the same unit test.
#
# ref: `TransactionManagementError “You can't execute queries until the end
#      of the 'atomic' block” while using signals, but only during Unit Testing
#      <https://stackoverflow.com/questions/21458387/transactionmanagementerror-you-cant-execute-queries-until-the-end-of-the-atom>`_    
#
# ... This is caused by a quirk in how transactions are handled in the newer
# versions of Django coupled with a unittest that intentionally triggers an exception ...
# 
# In Django 1.4, this works fine. However, in Django 1.5/1.6, each test
# is wrapped in a transaction, so if an exception occurs, it breaks the
# transaction until you explicitly roll it back. Therefore, any further
# ORM operations in that transaction, will fail with that
# django.db.transaction.TransactionManagementError exception.
    
import pdb
import pytz
import warnings

from datetime import datetime
from pathlib  import Path

from django.conf      import settings
from django.contrib.auth.models import User
from django.test import TestCase

from concurrency.exceptions import RecordModifiedError

from rstblog.models import Article
from rstblog.models import Author
from rstblog.models import Category

from rstblog.views import *

current_date = datetime(2018,1,15,tzinfo=pytz.utc)

author = None
category = None
article = None

ARTICLE_IT = ''':markup: restructuredtext
:language: it
:title: Avviare un progetto Django usando virtualenv
:created: 2018-05-01 15:36:30
:modified: 2018-05-01 15:36:30
:slug: avviare-progetto-django-usando-virtualenv
:category: information technology
:summary: Come avviare un progetto Django usando virtualenv.
:authors: Luciano De Falco Alfano

.. hic sunt leones

Avviare un progetto Django usando virtualenv
=====================================================

Una nota su come avviare un progetto Django usando virtualenv.
'''

ARTICLE_EN = ''':markup: restructuredtext
:language: en
:title: How start a Django project using virtualenv
:created: 2018-05-01 14:21:23
:modified: 2018-05-01 16:25:31
:slug: start-django-project-using-virtualenv
:Summary:  How start a new Django project using virtualenv. A note.
:Authors:   Luciano De Falco Alfano
:category: information technology
:translation_of: Avviare un progetto Django usando virtualenv

.. hic sunt leones

How start a Django project using virtualenv
=============================================

Just a quick note about starting up a Django environment using virtualenv.
'''

MEDIA_ROOT = os.path.join(settings.BASE_DIR, "testcontents", "media")

CONTENTS_ROOT = os.path.join(settings.BASE_DIR, "testcontents")

RSTBLOG = {
    'ARTICLES_DIR': os.path.join(settings.BASE_DIR, "testcontents", "articles"), 
    'START_CONTENT_SIGNAL': '.. hic sunt leones',     # WARNING: string on a single line, without other characters
    'languages': { 'it': 'italian',                   # 1st position is default language (functioning on py 3.6+)
                   'en': 'english', },
    'FIELDS': {'markup',
               'image',
               'atype',
               'language',
               'title',
               'created',
               'modified',
               'slug',
               'category',
               'published',
               'offer_home',
               'summary',
               'authors',
               'translation_of', },
    'LIST_FIELDS': {'authors',},
    'DT_FIELDS': { 'created',
                   'modified',},
    'BOOL_FIELDS': { 'published',
                     'offer_home', },
    'HOME_ITEMS': 10,
}

RSTSITE = {
    'PAGES_DIR': os.path.join(settings.BASE_DIR, "testcontents", "pages"), 
    'ABSTRACT': "django-rstblog test website", 
    'WTITLE': "django-rstblog test website", 
    'WSUBTITLE': "the programmer that misses the center of the target: haven't used code testing", 
}

P_ARTICLE = Path(CONTENTS_ROOT) / 'article.rst'
P_ARTICLE1 = Path(settings.RSTBLOG['ARTICLES_DIR']) / 'article.rst'
P_ARTICLE2 = Path(settings.RSTBLOG['ARTICLES_DIR']) / 'article.en.rst'

def setUpModule():
    '''test environment
    
    global _ENV describes it '''
    
    global author
    global article
    global category
    
    # redirect configuration directories to testcontents/...
    settings.MEDIA_ROOT = MEDIA_ROOT
    settings.RSTBLOG = RSTBLOG
    settings.RSTSITE = RSTSITE
    
    #pdb.set_trace()
    with P_ARTICLE.open(mode='wb') as article:
        article.write(ARTICLE_IT.encode('utf-8'))
    with P_ARTICLE1.open(mode='wb') as article:
        article.write(ARTICLE_IT.encode('utf-8'))
    with P_ARTICLE2.open(mode='wb') as article:
        article.write(ARTICLE_EN.encode('utf-8'))
    
    User.objects.create_superuser(username='luciano', password='luciano1234', email='email@address.com')
    
    author = Author( username = 'a.biagi', name = 'Antonio Biagi', )
    author.save()
    
    category = Category( name = 'uncategorized', )
    category.save()
    
    article = Article( title = 'un saggio di a.biagi',
        file='saggio_biagi.txt',
        category = category,
        slug='saggio_biagi', )
    article.save()
    article.authors.add(author)
    

def tearDownModule():
    P_ARTICLE.unlink()
    P_ARTICLE1.unlink()
    P_ARTICLE2.unlink()

    
from django.db import transaction


class CategoryModelTest(TestCase):

    def setUp(self):
        ''' setup from setUpModule'''
        pass
        
    def test_category_creation_1(self):
        '''test category model creation missing mandatory field'''
        
        # test mandatory field
        with self.assertRaises(Exception) as raised:
            c = Category(name=None)
            c.save()
        self.assertEqual("NOT NULL constraint failed: rstblog_category.name", str(raised.exception))
        
    def test_category_creation_2(self):
        ''' test category creation '''
        
        c = Category( name='categorized', )
        c.save()               # WARN: save before add ManyToMany rels
        self.assertIsInstance(c, Category)
        
        cs = Category.objects.all()
        self.assertEqual(len(cs), 2)

        
class AuthorModelTest(TestCase):

    def setUp(self):
        ''' setup from setUpModule'''
        
        pass
        
    def test_author_creation_1(self):
        '''test author model creation missing mandatory field'''
        
        # test mandatory field
        with self.assertRaises(Exception) as raised:
            a = Author(name=None)
            a.save()
        self.assertEqual("NOT NULL constraint failed: rstblog_author.name", str(raised.exception))
        
    def test_author_creation_2(self):
        ''' test author creation '''
        
        a = Author( name='autore', )
        a.save()               # WARN: save before add ManyToMany rels
        self.assertIsInstance(a, Author)
        
        a_s = Author.objects.all()
        self.assertEqual(len(a_s), 2)

        
class ArticleModelTest(TestCase):

    def setUp(self):
        ''' setup from setUpModule'''
        
        pass
        
    def test_article_creation_1(self):
        '''test article model creation missing mandatory field'''
        
        # test mandatory field, missing slug
        with self.assertRaises(Exception) as raised:
            t = Article(title=None, file='file', category=category)
            t.save()
        self.assertEqual("NOT NULL constraint failed: rstblog_article.title", str(raised.exception))
        # cannot insert a 2nd test about raise exception. needs a new method

    ## this test isn't functioning WHY?
    #def test_article_creation_2(self):
    #    '''test article model creation missing mandatory field'''
    #    
    #    # test mandatory field, missing category
    #    with self.assertRaises(Exception) as raised:
    #        t = Article(title='titolo', file='file', slug='titolo')
    #        t.save()
    #    self.assertEqual("NOT NULL constraint failed: rstblog_article.category_id", str(raised.exception))
        
    def test_article_creation_3(self):
        '''test article model creation missing mandatory field'''
        
        # test mandatory field, missing file
        with self.assertRaises(Exception) as raised:
            t = Article(title='titolo', file=None, category=category, slug='titolo')
            t.save()
        self.assertEqual("NOT NULL constraint failed: rstblog_article.file", str(raised.exception))
        
    def test_article_creation_4(self):
        ''' test article creation '''
        
        a = Article( title='articolo', file='file', category=category, slug='articolo')
        a.save()               # WARN: save before add ManyToMany rels
        self.assertIsInstance(a, Article)
        
        a_s = Article.objects.all()
        self.assertEqual(len(a_s), 2)

    def test_article_concurrency(self):
        ''' test course concurrency by  '''
        #pdb.set_trace()
        with self.assertRaises(Exception) as raised:  # top level exception as we want to figure out its exact type
            a1 = Article.objects.get(title='un saggio di a.biagi')
            a2 = Article.objects.get(title='un saggio di a.biagi')
            
            # chg zip => chg uploaded_at
            a1.summary = 'sommario a1'
            a2.summary = 'sommario a2'
            a1.save()
            a2.save()
        self.assertEqual(RecordModifiedError, type(raised.exception))  # if it fails, we'll get the correct type to import
        
        
#from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client
from django.utils.translation import activate
from django.contrib.auth import authenticate
        
        
class ViewsTest(TestCase):
    '''rstblog views tests'''

    def test_get_field(self):
        '''def get_field(area, field):'''
        area = ''':authors: Luciano De Falco Alfano
        '''
        field = 'authors'
        value = get_field(area, field)
        self.assertEqual(value, 'Luciano De Falco Alfano')
        
    def test_get_file_content(self):
        content = get_file_content(P_ARTICLE1)
        self.assertEqual(len(content.decode('utf-8')), len(ARTICLE_IT))
        self.assertEqual(content.decode('utf-8'), ARTICLE_IT)

    def test_separate(self):
        grand_content = ''':authors: Luciano De Falco Alfano

.. hic sunt leones

Avviare un progetto Django usando virtualenv'''
        fields, content = separate(grand_content)
        self.assertTrue('authors' in fields)
        self.assertTrue('Django' in content)
        
    def test_rough_docinfos(self):
        attributes = ''':markup: restructuredtext
:language: it
:title: Avviare un progetto Django usando virtualenv
:created: 2018-05-01 15:36:30
:modified: 2018-05-01 15:36:30
:slug: avviare-progetto-django-usando-virtualenv
:category: information technology
:summary: Come avviare un progetto Django usando virtualenv.
    Questa è una seconda riga.
:authors: Luciano De Falco Alfano'''
        rec = rough_docinfos(attributes)
        self.assertEqual(len(rec), 9)
        attributes = ''':markup: restructuredtext
:summaries: Come avviare un progetto Django usando virtualenv.
    Questa è una seconda riga.'''
        rec = rough_docinfos(attributes)
        self.assertEqual(len(rec), 1)
    
    def test_docinfos(self):
        c = Category(name='information technology')
        c.save()
        a = Author(username='Luciano', name='Luciano De Falco Alfano')
        a.save()
        attributes = ''':markup: restructuredtext
:language: it
:title: Avviare un progetto Django usando virtualenv
:created: 2018-05-01 15:36:30
:modified: 2018-05-01 15:36:30
:slug: avviare-progetto-django-usando-virtualenv
:category: information technology
:summary: Come avviare un progetto Django usando virtualenv.
    Questa è una seconda riga.
:authors: Luciano De Falco Alfano'''
        #pdb.set_trace()
        rec = docinfos(attributes)
        self.assertEqual(len(rec), 9)
        self.assertEqual(rec['category'], Category.objects.get(name='information technology'))
        self.assertEqual(rec['authors'][0], Author.objects.get(name='Luciano De Falco Alfano'))

        attributes = ''':markup: restructuredtext
:language: it
:title: Avviare un progetto Django usando virtualenv
:created: 2018-05-01 15:36:30
:modified: 2018-05-01 15:36:30
:slug: avviare-progetto-django-usando-virtualenv
:category: information technology
:summary: Come avviare un progetto Django usando virtualenv.
    Questa è una seconda riga.
:authors: Luciano De Falco Alfano
:translation_of: Start something'''
        #pdb.set_trace()
        rec = docinfos(attributes)
        self.assertEqual(len(rec), 10)
        self.assertEqual(rec['translation_of'], None)
        
    def test_get_record(self):
        '''get fields infos from file'''
        c = Category(name='information technology')
        c.save()
        a = Author(username='Luciano', name='Luciano De Falco Alfano')
        a.save()
        #pdb.set_trace()
        record, authors = get_record(P_ARTICLE1)
        self.assertEqual(len(record), 9)
        self.assertEqual(len(authors), 1)
    
    def test_load_article(self):
        '''def load_article(request):'''
        #activate('en')
        c = Client()
        login = c.login(username='luciano', password='luciano1234') 
        self.assertTrue(login)
        
        path = reverse(
            'rstblog:load_article',
            kwargs=dict(),
            )

        with P_ARTICLE.open(mode='rb') as fp:
            response = c.post(path, { 'article': fp}, follow=True, )
        #with open('tmp.html', 'w') as f:
        #    f.write(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('article article.rst loaded' in response.content.decode('utf-8'))
        
