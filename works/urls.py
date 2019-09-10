
from django.urls import path
from .views import WorkView, FileUploadView

app_name = "works"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('works/', WorkView.as_view()),
    path('upload/', FileUploadView.as_view()),
]