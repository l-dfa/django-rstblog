# rstblog/admin.py

from django.contrib import admin


from rstblog.models import Category
from rstblog.models import Author, AuthorAdmin
from rstblog.models import Article, ArticleAdmin


admin.site.register(Category)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Article, ArticleAdmin)
