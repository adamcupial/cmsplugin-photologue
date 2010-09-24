from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import *
from django.utils.translation import ugettext as _
from photologue.models import *
from django.conf import settings

#overrides photologue.urls.SAMPLE_SIZE : 'Number of random images from the gallery to display.'
SAMPLE_SIZE = ":%s" % getattr(settings, 'CMSPLUGIN_PHOTOLOGUE_SAMPLE_SIZE', 3)

class CMSPhotologueGalleryPlugin(CMSPluginBase):
    model = PhotologueGalleryPlugin
    name = _("Photologue Gallery")
    text_enabled = True
    render_template = "plugins/photologue_gallery.html"

    def render(self, context, instance, placeholder):
        context.update({'gallery':instance.gallery, 'placeholder':placeholder})
        context.update({'queryset': Gallery.objects.filter(is_public=True), 'allow_empty': True, 'paginate_by': 5, 'sample_size':SAMPLE_SIZE, 'css' : instance.get_css_display()})
        return context

plugin_pool.register_plugin(CMSPhotologueGalleryPlugin)


class CMSPhotologuePhotoPlugin(CMSPluginBase):
    model = PhotologuePhotoPlugin
    name = _("Photologue Photo")
    text_enabled = True
    render_template = "plugins/photologue_photo.html"
        
    def render(self, context, instance, placeholder):
        context.update({'photo':instance.photo, 'placeholder':placeholder})
        context.update({'slug_field': 'title_slug', 'queryset': Photo.objects.filter(is_public=True), 'is_thumb' : instance.is_thumb, 'css' : instance.get_css_display()})
        return context

plugin_pool.register_plugin(CMSPhotologuePhotoPlugin)