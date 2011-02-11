# -*- coding: utf-8 -*-
import django

if django.VERSION[0] >= 1 and django.VERSION[1] >=3:
    #Django 1.3+ -> No need to import cbv
    from django.views.generic import TemplateView
else:
    from cbv import TemplateView

class BaseShopView(TemplateView):
    '''
    A class-based view for use within the shop (this allows to keep the above
    import magic in only one place)
    
    As defined by http://docs.djangoproject.com/en/dev/topics/class-based-views/
    
    Stuff defined here (A.K.A this is a documentation proxy for the above link):
    -----------------------------------
    self.template_name : Name of the template to use for rendering
    self.get_context_data(): Returns the context {} to render the template with
    self.get(request, *args, **kwargs): called for GET methods
    ''' 