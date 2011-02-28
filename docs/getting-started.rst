================
Getting started
================

Here's the 1 minute guide to getting started with django SHOP and Django 1.2.x. 
Instructions for Django 1.3 will follow, but basically it means you don't need
django-cbv if you're using 1.3.

1. Create a normal Django project (we'll call it myshop for now)::
	
	django-admin startproject example
	cd example; django-admin startapp myshop
	
2. You'll want to virtualenv your world, just in case::
	
	virtualenv . ; source bin/activate
	pip install django-cbv
	
3. You'll be able to pip install later on, but for the time being it's manual::
	
	mkdir build; cd build; 
	git clone https://github.com/divio/django-shop.git ;
	cd django-shop; python setup.py install; cd ../..
	
4. Go to your settings.py and configure your DB like the following, or anything 
   matching your setup::
  
	DATABASES = {
    	'default': {
        	'ENGINE': 'django.db.backends.sqlite3',
        	'NAME': 'test.sqlite',                 
        	'USER': '',                      
        	'PASSWORD': '',                  
        	'HOST': '',                      
        	'PORT': '',           
    	}
	} 



5. Add the following stuff to middlewares::

	MIDDLEWARE_CLASSES = [
	    'django.middleware.common.CommonMiddleware',
	    'django.contrib.sessions.middleware.SessionMiddleware',
	    'django.middleware.csrf.CsrfViewMiddleware',
	    'django.contrib.auth.middleware.AuthenticationMiddleware',
	    'django.contrib.messages.middleware.MessageMiddleware',
	] # <-- Notice how it's a square bracket (a list)? It makes life easier.

	import django # A quick and very dirty test to see if it's 1.3 yet...
	if django.VERSION[0] < 1 or django.VERSION[1] < 3:
    	MIDDLEWARE_CLASSES.append('cbv.middleware.DeferredRenderingMiddleware')
	
6. Obviously, you need to add shop and myshop to your INSTALLED_APPS too::

	INSTALLED_APPS = [
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.sites',
	    'django.contrib.messages',
	    # Uncomment the next line to enable the admin:
	    'django.contrib.admin',
	    # Uncomment the next line to enable admin documentation:
	    'django.contrib.admindocs',
	    'shop', # The django SHOP application
	    'myshop', # the project we just created
	]
	
7. Make the example/urls.py contain the following::

	from shop import urls as shop_urls # <-- Add this at the top
	
	# Other stuff here
	
	urlpatterns = patterns('',
	    # Example:
	    #(r'^example/', include('example.foo.urls')),
	    # Uncomment the admin/doc line below to enable admin documentation:
	    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
	    # Uncomment the next line to enable the admin:
	    (r'^admin/', include(admin.site.urls)),
	    (r'^shop/', include(shop_urls)), # <-- That's the important bit
	)
	
7. Most of the stuff you'll have to do is styling and templates work, so go ahead
   and create a templates directory in your project::
   
	cd example/myshop; mkdir -p templates/myshop
	
8. Lock and load::

	cd .. ; python manage.py syncdb
	python manage.py runserver
	
9. Point your browser and marvel at the absence of styling::

	x-www-browser localhost:8000/shop

	
