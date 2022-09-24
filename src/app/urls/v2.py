from django.urls import include, path

urlpatterns = [
    path('auth/', include('a12n.urls')),
    path('banking/', include('banking.urls')),
    path('diplomas/', include('diplomas.urls')),
    path('homework/', include('homework.urls')),
    path('leads/', include('magnets.urls')),
    path('users/', include('users.urls')),
    path('notion/', include('notion.urls')),
    path('studies/', include('studying.urls')),
    path('orders/', include('orders.urls')),
    path('', include('products.urls')),

    path('healthchecks/', include('django_healthchecks.urls')),
    path('markdownx/', include('markdownx.urls')),
]
