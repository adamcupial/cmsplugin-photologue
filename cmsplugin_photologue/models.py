from django.db import models
from cms.models import CMSPlugin
from photologue.models import *
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

#get custom css from settings or use default
CMSPLUGIN_PHOTOLOGUE_CSS_CHOICES = getattr(settings,"CMSPLUGIN_PHOTOLOGUE_CSS", (('0', ''),('1', 'left'),('2', 'right'),('3', 'center'),) )


class PhotologueGalleryPlugin(CMSPlugin):
    gallery = models.ForeignKey(Gallery)
    css = models.CharField(_('CSS class'), max_length=1, choices=CMSPLUGIN_PHOTOLOGUE_CSS_CHOICES, default='0', help_text=_('Additional CSS class to apply'))

class PhotologuePhotoPlugin(CMSPlugin):
    IS_THUMB_CHOICES = (
        (u'0', u'No'),
        (u'1', u'Yes'),
    )
    photo = models.ForeignKey(Photo)
    is_thumb = models.CharField(_('is thumbnail'), max_length=1, choices=IS_THUMB_CHOICES, default='0', help_text=_('Show thumbnail or full size image'))
    css = models.CharField(_('CSS class'), max_length=1, choices=CMSPLUGIN_PHOTOLOGUE_CSS_CHOICES, default='0', help_text=_('Additional CSS class to apply'))
