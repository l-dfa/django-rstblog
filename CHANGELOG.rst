
############################
``django-rstblog`` changelog
############################

This file registers variations in the project ``django-rstblog``.

[next] - yyyy-mm-dd
======================

Added
--------------------

Changed
--------------------

Removed
--------------------


[0.1.2] - 2018-10-26
======================

Added
--------------------

* support of mathematical expressions in Markdown, using `python-markdown-math <https://pypi.python.org/pypi/python-markdown-math>`_
  and `mathjax <https://www.mathjax.org/>`_
* an article can link an image using the image field; this is shown in the article summary in home;

Changed
--------------------

* now the title of the blog home page is more meaning;
* in blog home, 1st article is more evident, others are on two columns;
* upgraded to Django ver 2.1.2;so:
  
  * changed login urls in urls.py due to change in Django;
  * mv templates/login.tml to templates/registration/login.html (as before);
  * changed @login_required in views.py, otherwise they were not functioning (as before);
  
[0.1.1] - 2018-09-24
======================

Added
--------------------

* documentation

Changed
--------------------

Removed
--------------------


[0.1.0] - 2018-09-22
======================

This is the initial release