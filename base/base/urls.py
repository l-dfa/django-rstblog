"""base URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf    import settings
from django.conf.urls.static import static
#from django.conf.urls.i18n   import i18n_patterns
from django.conf.urls        import url
from django.contrib import admin
from django.contrib.auth     import views as auth_views
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls    import include
from django.urls    import path

from . import views
from .sitemap import IndexSitemap
#from .sitemap import PagesSitemap
from .sitemap import MediaSitemap
from .sitemap import PlainSitemap
from rstblog.models import Article
from rstblog.models import Category

# this to create urls about search articles by categories
#    to pass to IndexSitemap in sitemaps section
search_by_category = []
try:
    categories = Category.objects.values_list('name', flat=True)
    for category in categories:
        search_by_category.append(['rstblog:index_category', category[:], 'article',])
except:
    pass

articles_dict = {
    # the next line is valid for articles AND pages
    #    so PageSitemap is no more needed
    'queryset': Article.objects.filter(published=True).order_by('-created'),
    'date_field': 'modified',
}

sitemaps= {
    'blog':  GenericSitemap(articles_dict, protocol='https', priority=0.5),
    'indexes': IndexSitemap(['rstblog:index',
                             'rstblog:show_stats',
                             ['rstblog:index_all_categories', 'article',],
                             *search_by_category,
                             ]),
    #'pages': PagesSitemap(['author.rst',
    #                       'formazione.rst',]),
    #'media': MediaSitemap(['pdfs/CV_luciano_de_falco_alfano-public-20180227.pdf',]),
    'plain': PlainSitemap(['robots.txt',
                           'sitemap.xml',]),
    
}

urlpatterns = [
    path('blog/', include('rstblog.urls', namespace='rstblog')),
    #path('load-page', views.load_page, name='load_page'),
    #path('show/<path:path>', views.show, name='show'),
    path('sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps, },
        name='django.contrib.sitemaps.views.sitemap', ),
    path('', views.index, name='index'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('login/', auth_views.login, {'template_name': 'login.html',}, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/login'}, name='logout'), 
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
