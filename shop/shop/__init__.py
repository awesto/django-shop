"""
See PEP 386 (http://www.python.org/dev/peps/pep-0386/)

Release logic:
 1. Increase version number in __version__ (below)
 2. Check that all changes have been documented in docs/changelog.rst
 3. In setup.py, assure that `classifiers` and `install_requires` reflect the latest versions.
 4. git add shop/__init__.py docs/changelog.rst setup.py
 5. git commit -m 'Bump to {new version}'
 6. git push
 7. assure that all tests pass on https://travis-ci.org/awesto/django-shop
 8. git tag {new version}
 9. git push --tags
10. python setup.py sdist
11. twine upload dist/django-shop-{new version}.tar.gz
"""
__version__ = '1.2.4'

default_app_config = 'shop.apps.ShopConfig'
