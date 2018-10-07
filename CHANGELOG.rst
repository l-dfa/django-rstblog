
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

* now the title of the blog home page is more meaning;
* in blog home, 1st article is more evident, others are on two columns;
* upgraded to Django ver 2.1.2,
  
  * changed login urls in urls.py due to change in Django;
  * mv templates/login.tml to templates/registration/login.html (as before);
  * changed @login_required in views.py, otherwise they were not functioning (as before);
  
* lost and recatched responsiveness;

Removed
--------------------

[0.1.0] - 2018-09-22
======================

This is the initial release