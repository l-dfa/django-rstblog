# rstblog/models.py
#     __name__ == 'rstblog.models'

import pdb
import pytz
import xml.etree.ElementTree as ET
from pathlib       import Path

#from datetime import date
from datetime import datetime

from django.contrib.auth.models import User
from django.db.utils   import IntegrityError
from django.core.exceptions import ValidationError
from django.conf       import settings
from django.db         import models
from django.urls       import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from concurrency.fields import IntegerVersionField

from .const import ARTICLES_DIR
from .const import LANGUAGES
from .const import TYPES
    
SHORT_LEN  = 50
MEDIUM_LEN = 250
LONG_LEN   = 2000

class Author(models.Model):
    '''author: article author
    
    fields:
        - name
        - last name
        - username
        - '''
    username = models.CharField(
        'username',
        max_length=SHORT_LEN,
        null=True,
        blank=True,
        default=None,
        unique=True,)
    name = models.CharField(
        'name',
        max_length=MEDIUM_LEN,
        null=False,
        blank=False,
        unique=True,)

    def __str__(self):
        return self.name

        
class Category(models.Model):
    '''category: article category
    
    fields:
        - name 
        
    initials: (how set them?)
        CATEGORIES = (
            'information tecnology',
            'opinion',
            'review',
            'science',
            'uncategorized',        )
    '''
        
    name = models.CharField(
        'name',
        max_length=SHORT_LEN,
        null=False,
        blank=False,
        unique=True,)
        
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"

        
    #def get_uncategorized(self):
    #    return Category.objects.get('uncategorized')


class Article(models.Model):
    '''article: blog article 
    
    fields:
        - title
        - created
        - file
        - language
        - markup
        - modified
        - summary
        - slug 
        - atype
        - published
        - home
        - hit
        - authors         m2m 
        - category        fKey
        - translation_of  fKey
        '''
    HTML  = 'html'
    MARKDOWN  = 'markdown'
    reST  = 'restructuredtext'
    MARKUP = (
        (HTML, 'html'),
        (MARKDOWN, 'markdown'),
        (reST, 'restructuredtext'),
    )
    title = models.CharField(
        'title',
        max_length=MEDIUM_LEN,
        null=False,
        blank=False,
        default='',
        unique=True,)
    created = models.DateTimeField(
        null=True,
        blank=True,
        default=None, )
    file = models.CharField(
        'file',
        max_length=MEDIUM_LEN,
        null=False,
        blank=False,
        unique=True, )
    image = models.CharField(
        'image',
        max_length=MEDIUM_LEN,
        null=False,
        blank=True,
        unique=False,
        default='', )
    language = models.CharField(
        'language',
        max_length = 2,
        null=False,
        blank = False,
        choices=list(LANGUAGES.items()),
        default = list(LANGUAGES.keys())[0], )  # BEWARE.from py 3.6+ dict preserve keys order by insertion
    markup = models.CharField(
        'markup_language',
        max_length = SHORT_LEN,
        null=False,
        blank = False,
        choices=MARKUP,
        unique=False,
        default = reST, )
    modified = models.DateTimeField(
        null=True,
        blank=True,
        default=None)
    summary = models.CharField(
        'summary',
        max_length=LONG_LEN,
        null=False,
        blank=True,
        default='', )
    slug = models.SlugField(
        'slug',
        max_length=MEDIUM_LEN,
        null=False,
        blank=False,
        unique=True,
        default=None, )
    atype = models.CharField(
        'type',
        max_length = SHORT_LEN,
        null=False,
        blank = False,
        choices=list(TYPES.items()),
        default=list(TYPES.keys())[0], )  # BEWARE.from py 3.6+ dict preserve keys order by insertion
    published = models.BooleanField(
        'published',
        null=False,
        blank = False,
        default=True, )
    offer_home = models.BooleanField(
        'offer article for home',
        null=False,
        blank = False,
        default=True, )
    image_in_content = models.BooleanField(
        'show article image in content',
        null=False,
        blank = False,
        default=True, )
    hit = models.IntegerField(
        'hit',
        null=False,
        blank=False,
        unique=False,
        default=0, )
    record_created  = models.DateTimeField(auto_now_add=True)
    record_modified = models.DateTimeField(auto_now=True)
    version = IntegerVersionField()     # manage optimistic lock
    
    authors = models.ManyToManyField(  # translators in case of translation_of
        Author,
        related_name='wrote',
        verbose_name='authors',
        blank=True,
        default=None, )
    category = models.ForeignKey(      # link to category
        Category,
        on_delete=models.SET_DEFAULT,
        null=False,
        blank=False,
        default=None,
        #default=get_uncategorized,    # how set default to UNCATEGORIZED?
        )
    translation_of = models.ForeignKey( # link to original article
        'self',
        on_delete=models.SET_DEFAULT,
        null=True,
        blank=True,
        related_name='translated_by',
        verbose_name='translation_of',
        default=None, )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.atype == 'article':
            return reverse('rstblog:show', args=[self.slug])
        elif self.atype == 'page':
            return reverse('show', args=[self.slug])
        else:
            raise ValueError(f'type {self.atype} not handled')
        
    def get_translations(self):
        #pdb.set_trace()
        if self.translation_of == None:
            original = self
            result = Article.objects.none()
        else:
            original = self.translation_of
            result = Article.objects.filter(pk=original.pk)
        result |= Article.objects.filter(translation_of=original.pk).exclude(pk=self.pk)
        return result
        
        
    def save(self, *args, **kwargs):
        try:
            c = self.category
        except:
            self.category = Category.objects.get(name='uncategorized')
        super().save(*args, **kwargs)    
        
        
    class Meta:
        ordering = ['-created']
        
                
from django import forms
from django.contrib import admin

# BEWARE: these must be after the definition of all the necessary models
#  so, they are at the end of this module
# this, and the next three, are derived from
# https://stackoverflow.com/questions/454436/unique-fields-that-allow-nulls-in-django
# about 'Unique fields that allow nulls in Django'
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'created', 'file', 'image',
            'language', 'markup', 'modified',
            'summary',
            'slug', 'atype', 'published', 'offer_home', 'hit',
            'authors', 
            'category',
            'translation_of',
            'image_in_content', )
    def clean_slug(self):
        return self.cleaned_data['slug'] or None

        
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm

    
class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('username', 'name', )
    def clean_username(self):
        return self.cleaned_data['username'] or None

        
class AuthorAdmin(admin.ModelAdmin):
    form = AuthorForm

    
    