

####################
django-rstblog
####################

``django-rstblog`` is a Django_ app to manage a blog, driven by articles written 
using reStructuredText_, or Markdown_ or HTML_.

The basic idea is to adopt a *hybrid* publication model,
halfway between a static site (pure html) and a dynamic one (all inside a DB,
as Wordpress_).

In practice, the author writes his article locally, at his/her PC, then

* he puts a series of lines at the top of the article; they serve to
  categorize it, indicating the language used, the title, and other attributes ...
* and a line of text, of fixed format, which separates the attributes from the 
  article content.

Finally he calls an address (URL) of the site that allows him to upload the article.
If the user is not logged in to the site, this address asks for user and password.

When the article is uploaded to the site, ``rstblog`` uses its attributes
to classify it in the database. The content of the article is not loaded
in the DB; when necessary, it is resumed from the file uploaded on the site.

If the author wants to modify the content of the article (or its attributes),
he edits the file on his PC, then upload it again.

Why use rstblog?
-----------------

What are the reasons that led us to this design choice? The following:

* we can always count on a local backup of all the contents of the site;
* we can work without an Internet connection, and connect only when
  we want to upload;
* the program is extremely light, it runs smoothly on servers with
  limited CPU capacity as with little RAM and HDU space (as long as accesses
  are contained, and we haven't this problem :-);
* we do not renounce the flexibility and speed of research that a DB allows;
* if we have a few articles [1]_ the DB can be implemented with the support library
  of Python (``sqlite3``), without using big programs (in the sense
  that they commit a lot of resources) as MySQL_, or PostgreSQL_, ...

Features
--------------

The features that the project currently implements are:

* the index of articles, indicating the number of consultations
  of each article and the main attributes;
* display of an article;
* upload of an article;
* complete reconstruction of the DB starting from the files of the articles uploaded to the site;
* administration of the DB contents using the Django's admin interface;
* articles may have translations, they can be present in more than one language;
* indication of site statistics; in the sense of how many articles are
  loaded, how many languages ​​are used, how many articles are present in each
  classification topic and language.

Cons
-------

What are the cons to the use of this environment? You must have a
good knowledge of Python/Django to:

* customize the project to your needs;
* install it in a production server.
  
A (not so) quick start
------------------------

0. With a virtual env activated, load the needed requirements::

    pip install django-rstblog
    
1. In your project setting.py file:

    1.1. Add ``rstblog`` to your INSTALLED_APPS like this::

        INSTALLED_APPS = [
            ...
            'django.contrib.sites',       # django's sites framework    
            'fullurl',                    # django-fullurl
            ...
            'rstblog',
        ]
    
    1.2. check for presence of login parameters::

        ...
        LOGIN_REDIRECT_URL = '/' # It means home view
        LOGIN_URL = '/login/'
        ...
    
    1.3. Add a RSTBLOG configuration section like this::
    
        RSTBLOG = {
            'ARTICLES_DIR': os.path.join(BASE_DIR, "contents", "articles"), 
            'START_CONTENT_SIGNAL': '.. hic sunt leones',     # BEWARE: string on a single line, without other characters
            'languages': { 'en': 'englis',                   # 1st position is default language (functioning on py 3.6+)
                           'it': 'italian', },
            'types': { 'article': 'article',                  # 1st position is default type (ok on py 3.6+)
                       'page': 'page', },
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
                           'modified', },
            'BOOL_FIELDS': { 'published',
                             'offer_home', },
            'HOME_ITEMS': 10,
        }
    
    1.4 check for presence of SITE_ID::
    
        ...
        SITE_ID = 1
        ...

2. In your project urls.py file:

    2.1. include the ``rstblog`` URLconf::

        from django.urls import include
        ...
        path('blog/', include('rstblog.urls', namespace='rstblog')),
    
    2.2. check for presence of login url::

        path('login/', auth_views.login, {'template_name': 'login.html',}, name='login'),

3. About your project templates:

    3.1. they must have a ``base.html`` template with this blocks
    used from rstblog templates::
    
        {% block title %}
        {% block meta %}
        {% block link %}
        {% block content %}
    
    3.2. check for the presence of login.html used in login.
    
4. In your project directory (where live manage.py), create the 
   directory ``contents/articles``

5. Run ``python manage.py migrate`` to create  the ``django-rstblog`` models.

6. Start the development server and visit http://127.0.0.1:8000/admin/
   to create at least a ``Category`` with value **uncategorized** to load articles
   (you'll need the Admin app enabled).
   
7. Start the development server and visit http://127.0.0.1:8000/blog/
   to show an empty list of articles.
   
8. Prepare an article on your PC as this one::

    :markup:   restructuredtext
    :title:    article
    :language: en
    :slug:     article
    :category: uncategorized
    
    .. hic sunt leones
    
    =========
    Article
    =========
    
    This is the article content.
    
    And this is a secod paragraph of the article.

9. Visit http://127.0.0.1:8000/blog/load-article to load the previous article.

10. Now, if you visit again http://127.0.0.1:8000/blog/ you get a list with
    an article, and if you click on title, you'll show it
    (url: http://127.0.0.1:8000/blog/show/article)

    
License
--------------

This work is distributed under a 
`MIT License <https://opensource.org/licenses/MIT>`_
license.


References
---------------

This project is `hosted on GitHub <https://github.com/l-dfa/django-rstblog.git>`_
Here you will find the complete environment
needed to develop the ``django-rstblog`` app. It means: not only the app, but
even a minimal django project that hosts it.

If you wish to see a website implemented using this app, you can navigate
to the `author's website <https://luciano.defalcoalfano.it>`_.

And the full documentation is
`hosted on Read the Docs <https://django-rstblog.readthedocs.io/>`_.


------------------------------

.. _Python: http://www.python.org/
.. _Django: https://www.djangoproject.com/
.. _MySQL: https://dev.mysql.com/downloads/
.. _PostgreSQL: https://www.postgresql.org/community/
.. _GitHub: https://github.com/

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: https://daringfireball.net/projects/markdown/syntax
.. _HTML: https://www.w3.org/TR/2017/REC-html52-20171214/
.. _Wordpress: https://wordpress.org/

.. [1] Not so few: with hundreds articles, everything reacts well.
  
