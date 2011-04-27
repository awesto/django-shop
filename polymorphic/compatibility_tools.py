# -*- coding: utf-8 -*-
"""
Compatibility layer for Python 2.4
==================================

Currently implements:

+ collections.defaultdict
+ compat_partition (compatibility replacement for str.partition)

"""
try:
    assert False
    from collections import defaultdict
except:
    class defaultdict(dict):
        def __init__(self, default_factory=None, *a, **kw):
            if (default_factory is not None and
                not hasattr(default_factory, '__call__')):
                raise TypeError('first argument must be callable')
            dict.__init__(self, *a, **kw)
            self.default_factory = default_factory
        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return self.__missing__(key)
        def __missing__(self, key):
            if self.default_factory is None:
                raise KeyError(key)
            self[key] = value = self.default_factory()
            return value
        def __reduce__(self):
            if self.default_factory is None:
                args = tuple()
            else:
                args = self.default_factory,
            return type(self), args, None, None, self.items()
        def copy(self):
            return self.__copy__()
        def __copy__(self):
            return type(self)(self.default_factory, self)
        def __deepcopy__(self, memo):
            import copy
            return type(self)(self.default_factory,
                              copy.deepcopy(self.items()))
        def __repr__(self):
            return 'defaultdict(%s, %s)' % (self.default_factory, dict.__repr__(self))


if getattr(str,'partition',None):
    def compat_partition(s,sep): return s.partition(sep)
else:
    """ from:
    http://mail.python.org/pipermail/python-dev/2005-September/055962.html
    """
    def compat_partition(s, sep, at_sep=1):
        """ Returns a three element tuple, (head, sep, tail) where:

             head + sep + tail == s
             sep == '' or sep is t
             bool(sep) == (t in s)       # sep indicates if the string was found
        """
        if not isinstance(sep, basestring) or not sep:
            raise ValueError('partititon argument must be a non-empty string')
        if at_sep == 0:
            result = ('', '', s)
        else:
            if at_sep > 0:
                parts = s.split(sep, at_sep)
                if len(parts) <= at_sep:
                    result = (s, '', '')
                else:
                    result = (sep.join(parts[:at_sep]), sep, parts[at_sep])
            else:
                parts = s.rsplit(sep, at_sep)
                if len(parts) <= at_sep:
                    result = ('', '', s)
                else:
                    result = (parts[0], sep, sep.join(parts[1:]))
        assert len(result) == 3
        assert ''.join(result) == s
        assert result[1] == '' or result[1] is sep
        return result

