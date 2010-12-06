# This shouldn't be used yet obviously, there is nothing to build :)

setup(
    author="Christopher Glass",
    author_email="tribaal@gmail.com",
    name='django-shop',
    version='0.0.0',
    description='An Advanced Django Shop',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='http://www.django-shop.org/',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    requires=[
        'django (>1.1.0)',
    ],
    packages=find_packages(exclude=["example", "example.*"]),
#    package_data={
#        'cms': [
#            'templates/admin/*.html',
#            'templates/admin/cms/mail/*.html',
#            'templates/admin/cms/mail/*.txt',
#            'templates/admin/cms/page/*.html',
#            'templates/admin/cms/page/*/*.html',
#            'templates/cms/*.html',
#            'templates/cms/*/*.html',
#            'plugins/*/templates/cms/plugins/*.html',
#            'plugins/*/templates/cms/plugins/*/*.html',
#            'plugins/*/templates/cms/plugins/*/*.js',
#            'locale/*/LC_MESSAGES/*',
#        ] + media_files,
#        'example': [
#            'media/css/*.css',
#            'media/img/*.jpg',
#            'templates/*.html',
#            'sampleapp/media/sampleapp/img/gift.jpg',
#            'sampleapp/templates/sampleapp/*.html',
#        ],
#        'menus': [
#            'templates/menu/*.html',
#        ],
#    },
    zip_safe = False
)

