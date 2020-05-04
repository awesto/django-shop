"""
See PEP 386 (http://www.python.org/dev/peps/pep-0386/)

Release logic:
 1. Increase version number in __version__ (below)
 2. Check that all changes have been documented in docs/changelog.rst
 3. git add shop/__init__.py docs/changelog.rst
 4. git commit -m 'Bump to {new version}'
 5. git push
 6. assure that all tests pass on https://travis-ci.org/awesto/django-shop
 7. git tag {new version}
 8. git push --tags
 8. python setup.py sdist
10. twine upload dist/django-shop-{new version}.tar.gz
"""
__version__ = '1.2.dev'

default_app_config = 'shop.apps.ShopConfig'
