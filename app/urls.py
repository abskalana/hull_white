from django.conf.urls import url

from app import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^test/', views.auto_generate, name='test'),
    url(r'^about/', views.about, name='about'),
    url(r'^document/', views.documentation, name='document'),
    url(r'^api/hullwhite/', views.api_hullwhite, name='api_hull_white'),
    url(r'^api/test/auto/', views.api_hullwhite_auto, name='api_hull_white_auto'),
]
