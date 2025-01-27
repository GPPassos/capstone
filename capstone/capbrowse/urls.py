from . import views
from django.urls import path

urlpatterns = [
    ### pages ###
    path('view/court/<int:court_id>/', views.view_court, name='view_court'),
    path('view/reporter/<int:reporter_id>/', views.view_reporter, name='view_reporter'),
    path('view/jurisdiction/<int:jurisdiction_id>/', views.view_jurisdiction, name='view_jurisdiction'),
    path('search/', views.search, name='search'),
    path('trends/', views.trends, name='trends'),
]

