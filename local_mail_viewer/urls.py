from django.urls import path

from local_mail_viewer import views

app_name = 'mail'

urlpatterns = [
    path('', views.mail_list, name='mails'),
    path('detail/<str:filename>/', views.mail_detail, name='mail-detail'),
    path('delete/<str:filename>/', views.mail_delete, name='delete'),
    path('delete/', views.mail_delete_all, name='delete_all'),
    path(
        'download-attachment/<str:filename>/<str:name>/',
        views.download_attachment,
        name='mail-attachment'
    ),
]
