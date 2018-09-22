.. rstblog documentation master file, created by
   sphinx-quickstart on Fri Jul 27 11:42:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to rstblog documentation
===================================

``rstblog`` project is about a simple blog driven by articles written
using reStructuredText markup language.

This is its documentation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   Article author manual       <author_manual/author_manual>
   (Empty) Site manager manual         <manager_manual/manager_manual>
   (Empty) Details about how it works  <programmer_manual/programmer_manual>
   
General introduction
-----------------------

This project is developed using Django_, a web framework based on the
Python_ language. And this fact is important to you *only if you
wish to modify how the project work*. In other words if you need to change 
the programming code of the project.

Central to this work is also the reStructuredText_ markup language (for
short: reST from now on). This is a method to sign a text achieving formatting effects, as 
writing charactes in bold, or creating a table, or an html link
to another document.

And this fact is important to you as a user of this project. Why? we'll see.

Let's assume you have an ``rstblog`` installation functioning and 
responding to address ``https://my.blog.org`` (original, isn't it?).
And, of corse, you know a username (& password) authorized to publish 
an article on it.

Well, now you have a fantastic idea you need to share with mankind.

First think first: you write a vibrant article using your favourite
text editor in your computer, formatting it using *reST* [#]_.
Note: by now your work is saved in a file on your PC.

When you are satisfied of your article, using your web browser, you
navigate to ``https://my.blog.org/blog/load-article``.

``rstblog`` will request your username and password. If you feed them, it
will request to you what file you need to load. Browse to it
and click the send button. ``rstblog`` will respond you: *article xxx loaded* [#]_

We are done: homepage at ``https://my.blog.org`` will show the title
and summary of your new article. And if you click on title, you'll
see your article in all its glory.

Well, there is some little trick to use to obtain the right result. But
I swear: it's all very simple. Otherwise I would not be able to use it.

Now. I imagine you are asking yourself: "for God's sake: why I need
use a text editor and upload a file to my site, if wordpress_ or
drupal_ allow me to write it directly in the browser window?".

Due to some reasons.

First of all: never appened while you are writing, something goes wrong (
power failure at your adsl router, a timeout to your server, ...) and do you
risk to loose your work? It appened to me. From that moment on, I got used to write 
long articles in files *before* to feed drupal with them.

*But* ... this habit lead to different use of the tools. Long articles
initially written by files. The short ones written directly using
the user interface of the blog, without a local file in your computer.

And when you need to make a little correction to an article, for sure
you'll do it using the blog user interface. So your local file in a moment
will no longer be aligned with the online version of your article.

So you ask to me: "where is the problem?". The problem is the fact that your
articles are stored partially only in the database of your blog software. Partially 
because probably images, and other files that your refer to into your articles
are in the web server file system. So you need to backup all these informations
and wish you will not have to change the blog software, or you might 
encounter some (big) problems to transfer them from one kind of system to the other.

Again: *but* ... if there is a think I know working in IT for over 30 years
is that *for sure* your data will have to change system type. Every type
of system type :-). Even not only the name of software (e.g. from Drupal to 
Wordpress), but from type of software to another (e.g. from specialized Blog to general 
purpouse CMS), or even more complex scenarios.

In these cases, you have more chance of success if your data are in some
form of *source* format. The simpler it is, the better it is.

So, returning to us, I decided to experiment to use a simple
markup language, as reSt, or markdown, to write a local copy of the
articles. And, while I'm living a full copy of them on my PC
(this is a local backup, from start!), I upload
them to a web server able to host them and catalog their contents
by some simple fields written in the article file text.

So, in case of restore in other server I can load my local copy. And in case 
of a radical software change, I can think to write some (hopefully) simple
interface to load my files in a future shocking AI.

If this long introduction did not make you escape, and you are still
interested to know better how use ``rstblog``, I can propose you
these chapters:

* an article :ref:`author manual`;
* an **empty** site :ref:`manager manual`;
* an **empty** :ref:`programmer manual`.


References
-----------------------

This project is open source `hosted on GitHub <https://github.com/l-dfa/base_rstblog>`_.

And here there is the `author's website <https://luciano.defalcoalfano.it>`_.
Its contents are mainly written in italian language.

This is the `launch article <https://luciano.defalcoalfano.it/blog/show/rstblog-project>`_
about this project.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _Python: http://www.python.org/
.. _Django: https://www.djangoproject.com/

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _a primer to reST: http://docutils.sourceforge.net/docs/user/rst/quickstart.html
.. _markdown: https://daringfireball.net/projects/markdown/syntax
.. _html: https://www.w3.org/TR/2017/REC-html52-20171214/
.. _wordpress: https://wordpress.org/
.. _drupal: https://www.drupal.org/

.. [#] To be honest, you can also use markdown_, or html_ too. But we are
   a little fanatic about reST; so: this is a link to `a primer to reST`_.
   
.. [#] Or, in case of error, it will prompt you.