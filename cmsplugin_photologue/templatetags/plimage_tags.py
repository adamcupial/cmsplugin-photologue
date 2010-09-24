from django import template
from photologue.models import PhotoSize, Photo
register = template.Library()

from django import template
from photologue.models import PhotoSize, Photo
register = template.Library()

def render_pl_image(picture, size):
    if not isinstance(picture,Photo):
        raise template.TemplateSyntaxError, "render_pl_image tag's first argument must"\
        " be and instance of photologue photo"
    if not isinstance(size,PhotoSize):
        raise template.TemplateSyntaxError, "render_pl_image tag's second argument must"\
        " be and instance of photologue photosize"
    
    try:
        image_url_method = getattr(picture,'get_'+size.name+'_url')
    except AttributeError:
        image_url_method = getattr(picture,'get_thumbnail_url')
        
    try:
        image_size_class = getattr(picture,'get_'+size.name+'_size')
        image_size = image_size_class()
    except AttributeError:
        image_size = None
        
    url = image_url_method()
     
    if image_size:
        return '<img src="%s" alt="%s" width="%s" height="%s"/>' % (url, picture.title,image_size[0], image_size[1])
    elif size.crop:
        return '<img src="%s" alt="%s" width="%s" height="%s"/>' % (url, picture.title,size.width, size.height)
    else:
        return '<img src="%s" alt="%s" />' % (url, picture.title)

register.simple_tag(render_pl_image)