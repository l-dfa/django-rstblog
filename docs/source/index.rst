.. django-rstblog documentation master file, derived from rstblog
   project master file.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ``django-rstblog`` documentation
=============================================

``django-rstblog`` is a Django_ app to manage a blog, driven by articles written 
using reStructuredText_, or Markdown_ or HTML_.

This is its documentation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   Article author manual       <author_manual/author_manual>
   Site manager manual         <manager_manual/manager_manual>
   
General introduction
-----------------------

The basic idea is to adopt a *hybrid* publication model,
halfway between a static site (pure html) and a dynamic one (all inside a DB,
as Wordpress_).

In practice, the author writes his article locally, at his/her PC, then

* he puts a series of lines of text at the top of the article; they serve to
  categorize it, indicating the language used, the title, and other attributes ...
* and a line of text, of fixed format, which separates the attributes from the 
  article content.

Finally he calls an address (URL) of the site that allows him to upload the article.
If the user is not logged in to the site, this address asks for username and password.

When the article is uploaded to the site, ``django-rstblog`` uses its attributes
to classify it in the database. The content of the article is not loaded
in the DB; when necessary, it is resumed from the file uploaded on the site.

If the author wants to modify the content of the article (or its attributes),
he edits the file on his PC, then upload it again.

Why use ``django-rstblog``?
---------------------------------

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

The features that the app currently implements are:

* the index of articles, indicating the number of consultations
  of each article and the main attributes;
* display of an article;
* upload of an article;
* complete reconstruction of the DB starting from the files of the articles uploaded to the site;
* administration of the DB contents using the Django's admin interface; use this interface to:

    * manage a list of authors of the articles;
    * manage a list or arguments to classify the articles (an article must 
      belong to an argument);
      
* articles may have translations, they can be present in more than one language;
* indication of site statistics; in the sense of how many articles are
  loaded, how many languages ​​are used, how many articles are present in each
  classification topic and language.
  
Note that, at least by now, ``django-rstblog`` is capable to manage sites with 
a single blog. It isn't developed to manage multi-blogs sites.

Cons
-------

What are the cons to the use of this environment? You must have a
good knowledge of Python/Django:

* to customize the app to your needs;
* to install it in a django project and in a production server.
  
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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

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
  
