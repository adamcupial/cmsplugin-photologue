from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from cms.utils.navigation import NavigationNode
from photologue.models import Gallery, Photo
from photologue.urls import gallery_args, photo_args


def get_nodes(request):
    """ creates mptt style parent-child list for extending django-cms navigation (menu & breadcrumb); structured on photologue.urls """

    res = []                                                        #NavigationNode result list

    for q in gallery_args, photo_args:                              #get public Galleries & Photos
        if q.has_key('queryset'):                                   #use default querysets from photologue.urls
            queryset = q['queryset']
            try:                                                    #get the name of the queryset's model
                model = q['queryset'][0].__class__.__name__.lower()
            except IndexError:                                      #abort if empty
                return res

            #check if multilingual middleware is installed
#            from django.conf import settings
#            if 'cms.middleware.multilingual.MultilingualURLMiddleware' in settings.MIDDLEWARE_CLASSES:
#                multilingual = True
##                from django.utils.translation import get_language
#                from django.utils.translation import get_language_from_request
#                import ipdb; ipdb.set_trace()
#                lang_namespace = "%s:" % get_language_from_request(request)
#            else:
#                lang_namespace = ''

        else:
            return res


        #create the base path of the URL ('gallery/' or 'photo/')
        base_node = NavigationNode(model, reverse('pl-%s-archive' % model,))
#        base_node = NavigationNode(model, reverse('%spl-%s-archive' % (lang_namespace, model)))
        base_node.childrens = []

        #create node for object_list view (photologue uses this view for pagination)
        #urlpattern to match: url(r'^photo/page/(?P<page>[0-9]+)/$', 'object_list', {'queryset': Photo.objects.filter(is_public=True), 'allow_empty': True, 'paginate_by': 20}, name='pl-photo-list'),
        #path example: request.META['PATH_INFO'] = u'/galleries/photo/page/2/'  or  u'/galleries/gallery/page/1/'
        try:
            #page_path gets the relevant parts of the path for paging
            page_path = request.META['PATH_INFO'].split('/')[-4:-1]     #eg: '/mygalleries/gallery/page/1/' ->  ['gallery', 'page', '1']
            #execute only if page_path is a photologue paged url for this model
            assert len(page_path) == 3 and [model, 'page', str(int(page_path[2]))] == page_path
            #name the node with a string, reverse to the paged named url, and pass the page value from page_path
            pages_node = NavigationNode('page %s' % page_path[2], reverse('pl-%s-list' % model, kwargs=dict(page=page_path[2])))
#            pages_node = NavigationNode('page %s' % page_path[2], reverse('%spl-%s-list' % (lang_namespace, model), kwargs=dict(page=page_path[2])))
            #modify url used in href, this doesn't work because NavigationNode uses the passed url for get_absolute_url
            pages_node.get_absolute_url = lambda: reverse('pl-%s-list' % model, kwargs=dict(page=1))
#            pages_node.get_absolute_url = lambda: reverse('%spl-%s-list' % (lang_namespace, model), kwargs=dict(page=1))
            #attach the node to the main list
            base_node.childrens.append(pages_node)
        except:
            #fail silently if not applicable
            pass

        #create NavigationNodes for the queryset
        for item in queryset:

            years_done = []                                             #keeps track of published item years
            months_done = []
            days_done = []
            slug_done = []
            page_done = []

            #get the date for this query object; 'date_added' called 'date published' in photologue admin
            date = item.date_added

            if not date.year in years_done:                         #if this year is not in the years_done list
                years_done.append(date.year)                        #add it to years_done list
                #name the navigation node with the item's year, reverse to a named url, and pass the value captured by url regex
                year_node = NavigationNode(date.year, reverse('pl-%s-archive-year' % model, kwargs=dict(year=date.year)))
#                year_node = NavigationNode(date.year, reverse('%spl-%s-archive-year' % (lang_namespace, model), kwargs=dict(year=date.year)))
                year_node.childrens = []                            #create childrens sublist for this year
                months_done = []                                    #keeps track of published item months for this year
                base_node.childrens.append(year_node)                               #add this NavigationNode to the main list

            if not date.month in months_done:
                months_done.append(date.month)
                month_node = NavigationNode(date.strftime('%b').lower(), reverse('pl-%s-archive-month' % model, kwargs=dict(year=date.year, month=date.strftime('%b').lower())))
#                month_node = NavigationNode(date.strftime('%b').lower(), reverse('%spl-%s-archive-month' % (lang_namespace, model), kwargs=dict(year=date.year, month=date.strftime('%b').lower())))
                month_node.get_menu_title = date.strftime('%m')     #use double int month name for menus
                month_node.childrens = []
                days_done = []
                year_node.childrens.append(month_node)

            if not date.day in days_done:
                days_done.append(date.day)
                day_node = NavigationNode(date.day, reverse('pl-%s-archive-day' % model, kwargs=dict(year=date.year, month=date.strftime('%b').lower(), day=date.day)))
#                day_node = NavigationNode(date.day, reverse('%spl-%s-archive-day' % (lang_namespace, model), kwargs=dict(year=date.year, month=date.strftime('%b').lower(), day=date.day)))
                day_node.childrens = []
                slug_done = []
                month_node.childrens.append(day_node)

            if not item.title_slug in slug_done:
                slug_done.append(item.title_slug)
                #one node child for the day node
                item_node = NavigationNode(item.title, reverse('pl-%s-detail' % model, kwargs=dict(year=date.year, month=date.strftime('%b').lower(), day=date.day, slug=item.title_slug)))
#                item_node = NavigationNode(item.title, reverse('%spl-%s-detail' % (lang_namespace, model), kwargs=dict(year=date.year, month=date.strftime('%b').lower(), day=date.day, slug=item.title_slug)))
                day_node.childrens.append(item_node)
                #and finally, one node child for the base node
                item_node = NavigationNode(item.title, reverse('pl-%s' % model, kwargs=dict(slug=item.title_slug)))
#                item_node = NavigationNode(item.title, reverse('%spl-%s' % (lang_namespace, model), kwargs=dict(slug=item.title_slug)))
                base_node.childrens.append(item_node)

        res.append(base_node)

    return res