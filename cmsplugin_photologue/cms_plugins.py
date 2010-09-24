from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import *
from django.utils.translation import ugettext as _
from photologue.models import *
from django.conf import settings

class CMSPhotologueGalleryPlugin(CMSPluginBase):
    model = PhotologueGalleryPlugin
    name = _("Photologue Gallery")
    text_enabled = True
    render_template = "plugins/cmsplugin_photologue/photologue_gallery.html"

    def render(self, context, instance, placeholder):
        photos = instance.gallery.photos.filter(is_public=True)
        
        if instance.randomize:
            photos.order_by('?')
        else:
            photos.order_by('-date_added')
           
        
        
        if instance.limit != 0:
            photos = photos[:instance.limit]
        context.update({'photos':photos,
                        'gallery':instance.gallery,
                        'placeholder':placeholder})
        context.update({'allow_empty': True,
                        'paginate_by': 5,
                        'css' : instance.get_css_display(),
                        'show_title':instance.show_title,
                        'show_caption':instance.show_caption,
                        'link_to_full_image':instance.link_to_full_image,
                        'link_to_gallery':instance.link_to_gallery,
                        'size':instance.size,
                        })
        return context

plugin_pool.register_plugin(CMSPhotologueGalleryPlugin)


class CMSPhotologuePhotoPlugin(CMSPluginBase):
    model = PhotologuePhotoPlugin
    name = _("Photologue Photo")
    text_enabled = True
    render_template = "plugins/cmsplugin_photologue/photologue_photo.html"
        
    def render(self, context, instance, placeholder):
        context.update({'photo':instance.photo, 'placeholder':placeholder})
        context.update({'slug_field': 'title_slug',
                        'size' : instance.size,
                        'show_caption':instance.show_caption,
                        'link_to_full_image':instance.link_to_full_image,
                        'css' : instance.get_css_display(),
                        'queryset':Photo.objects.filter(is_public=True)})
        return context

plugin_pool.register_plugin(CMSPhotologuePhotoPlugin)