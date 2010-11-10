from django.db import models
from cms.models import CMSPlugin, Page
from photologue.models import *
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

#get custom css from settings or use default
CMSPLUGIN_PHOTOLOGUE_CSS_CHOICES = getattr(settings,"CMSPLUGIN_PHOTOLOGUE_CSS",
                                           (('0', ''),
                                            ('1', 'left'),
                                            ('2', 'right'),
                                            ('3', 'center'),) )


class PhotologueGalleryPlugin(CMSPlugin):
    gallery = models.ForeignKey(Gallery,verbose_name=_('Gallery'))
    link_to_gallery = models.BooleanField(verbose_name=_('Link to gallery?'))
    show_title = models.BooleanField(verbose_name=_('Show gallery title?'))
    randomize = models.BooleanField(verbose_name=_('Show random images?'),
                                    help_text=_('If unchecked images will be sorted according to the date'))
    show_caption = models.BooleanField(verbose_name=_('Show caption?'))
    link_to_full_image = models.BooleanField(
        verbose_name=_('Link to full image?'))
    limit = models.PositiveIntegerField(default=0,
                                        verbose_name=_('Gallery sample limit'),
                                        help_text=_('0 - unlimited'))
    size = models.ForeignKey(PhotoSize,verbose_name=_('Photo size'))
    css = models.CharField(max_length=1,
                           choices=CMSPLUGIN_PHOTOLOGUE_CSS_CHOICES,
                           default='0',
                           help_text=_('Additional CSS class to apply'),
                           verbose_name=_('CSS class'))

class PhotologuePhotoPlugin(CMSPlugin):
    photo = models.ForeignKey(Photo,verbose_name=_('Photo'))
    page_link = models.ForeignKey(
        Page, 
        verbose_name=_("page"), 
        help_text=_("If present image will be clickable"), 
        blank=True, 
        null=True, 
        limit_choices_to={'publisher_is_draft': True}
    )
    show_caption = models.BooleanField(verbose_name=_('Show caption?'))
    link_to_full_image = models.BooleanField(verbose_name=_('Link to full image?'))
    size = models.ForeignKey(PhotoSize,verbose_name=_('Photo size'))
    css = models.CharField(max_length=1,
                           choices=CMSPLUGIN_PHOTOLOGUE_CSS_CHOICES,
                           default='0',
                           help_text=_('Additional CSS class to apply'),
                           verbose_name=_('CSS class'))
