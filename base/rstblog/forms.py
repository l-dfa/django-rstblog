# rstblog/forms.py

from django import forms

from .models import Article


class LoadArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ( 'file', )

