
.. _programmer manual:

programmer manual
=================

.. contents:: programmer manual table of contents
   :depth: 2
   


load article
-------------------

This is necessary in two different context:

* while loading a single article
* while rebuilding the table of articles starting from list of
  article files hosted in server file system
  
loading a single article
^^^^^^^^^^^^^^^^^^^^^^^^^

Here we need:

* upload_file from client to server file system
* create (or update) article record in DB from uploaded file

rebuilding the table of articles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We:

* list all the article files in server file system
* cicling on previous list, for every original file:

  * create article record in DB
  
* cicling again on previous list, for every translation file:

  * create article record in DB
  
So we can see: there is a function *create article record in DB*
used in both the context.