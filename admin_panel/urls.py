from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='admin_dashboard'),
    path('articles/', views.ArticleListView.as_view(), name='admin_articles'),
    path('articles/edit/<pk>', views.ArticleEditView.as_view(), name='admin_edit_articles'),
]
