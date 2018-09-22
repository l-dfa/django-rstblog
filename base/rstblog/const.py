# rstblog/const.py

from pathlib       import Path

from django.conf      import settings

__version__ = '0.1.1'

try:
    ARTICLES_DIR = Path(settings.RSTBLOG['ARTICLES_DIR'])
except:
    ARTICLES_DIR = Path(settings.BASE_DIR) / 'contents/articles'

try:
    PAGES_DIR = Path(settings.RSTSITE['PAGES_DIR'])
except:
    PAGES_DIR = Path(settings.BASE_DIR) / 'contents/pages'

try:
    START_CONTENT_SIGNAL = settings.RSTBLOG['START_CONTENT_SIGNAL']
except:
    START_CONTENT_SIGNAL = '.. hic sunt leones'
    
try:
    LANGUAGES = settings.RSTBLOG['languages']
except:
    LANGUAGES = { 'en': 'english',
                  'it': 'italian', }

try:
    TYPES = settings.RSTBLOG['types']
except:
    TYPES = { 'article': 'article',
                  'page':    'page', }

try:
    HOME_ITEMS = settings.RSTBLOG['HOME_ITEMS']
except:
    HOME_ITEMS = 10
                  
class SUFFIX(object):
    reST = '.rst'
    markdown = '.md'
    html = '.html'
    text = '.txt'
