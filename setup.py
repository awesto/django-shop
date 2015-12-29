from setuptools import setup, find_packages
import shop
try:
    from pypandoc import convert
except ImportError:
    def convert(filename, fmt):
        with open(filename) as fd:
            return fd.read()

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

setup(
    author="Jacob Rief",
    author_email="jacob.rief@gmail.com",
    name="django-shop",
    version=shop.__version__,
    description="A RESTful Django Shop",
    long_description=convert('README.md', 'rst'),
    url='http://www.django-shop.org/',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=['example', 'docs', 'tests']),
    include_package_data=True,
    zip_safe=False,
)
