# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
See PEP 386 (http://www.python.org/dev/peps/pep-0386/)

Release logic:
1. Remove "dev" from current.
2. git commit
3. git tag <version>
4. push to pypi + push to github
5. bump the version, append '.dev0'
6. git commit
7. push to github (to avoid confusion)
"""
__version__ = '0.9.0rc1'

default_app_config = 'shop.apps.ShopConfig'
