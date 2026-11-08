from django.contrib import admin
from django.urls import path

admin.site.index_template = "admin/blog/dashboard.html"

urlpatterns = [
    path('admin/', admin.site.urls),
]