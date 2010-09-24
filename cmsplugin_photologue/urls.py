#url bridge for django-cms2 to django-photologue
#include this module in your django-cms2 project's settings.py
#eg: CMS_APPLICATIONS_URLS = ( ('cmsplugin_photologue.urls', 'Photologue plugin app'), )

from django.conf.urls.defaults import *
from django.conf import settings


#get variables defined in photologue.urls
from photologue.urls import gallery_args

#import photologue urls
urlpatterns = patterns('',
    url(r'^', include('photologue.urls')),
)

#add urlpattern to display gallery list for the root request (not defined in photologue.urls)
urlpatterns += patterns('django.views.generic.date_based',
#   url(r'^/?$', 'archive_index', gallery_args, name='pl-gallery-archive',),
    #not naming this urlpattern, so it doesn't conflict with identically named urlpattern in photologue.urls
   url(r'^/?$', 'archive_index', gallery_args, ),
)