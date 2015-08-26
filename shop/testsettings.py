SECRET_KEY = 'test'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'treebeard',
    'cms',
    'post_office',
    'filer',
    'shop',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
)

SHOP_APP_LABEL = 'testshop'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
