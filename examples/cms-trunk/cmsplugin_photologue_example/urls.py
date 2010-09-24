from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

admin.site.root_path = "/admin/" # there is probably a bug in django...

urlpatterns = patterns('',
    #(r'^admin/(.*)', admin.site.root),
    (r'^admin/', include(admin.site.urls)),
    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
    
    # just for testing - native way to sampleapp urls 
    # (r'^sampleapp-native/', include('sampleapp.urls')),
)

if settings.DEBUG:
    urlpatterns+= patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True})
    )

urlpatterns += patterns('',
    url(r'^', include('cms.urls')),
)