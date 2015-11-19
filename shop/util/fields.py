# -*- coding: utf-8 -*-
from decimal import Decimal
from django.db.models.fields import DecimalField


class CurrencyField(DecimalField):
    """
    A CurrencyField is simply a subclass of DecimalField with a fixed format:
    max_digits = 30, decimal_places=2, and defaults to 0.00
    """
    def __init__(self, **kwargs):
        defaults = {
            'max_digits': 30,
            'decimal_places': 2,
            'default': Decimal('0.0')
        }
        defaults.update(kwargs)
        super(CurrencyField, self).__init__(**defaults)

    def south_field_triple(self):  # pragma: no cover
        """
        Returns a suitable description of this field for South.
        This is excluded from coverage reports since it is pretty much a piece
        of South itself, and does not influence program behavior at all in
        case we don't use South.
        """
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.DecimalField"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)


def upload_to_classname(instance, filename):
    basedir = str(instance.__class__.__name__).lower()
    ext = os.path.splitext(filename)[1]
    filename = None

    if not filename and hasattr(instance, "slug") and getattr(instance, "slug"):
        filename = getattr(instance, "slug")

    if not filename and instance.pk:
        filename = "image_" + str(instance.pk)

    if not filename:
        filename = "image_" + str(random.randint(1000, 1000000))
        while os.path.exists(os.path.join(settings.MEDIA_ROOT, basedir, filename + ext)):
            filename = "image_" + str(random.randint(1000, 1000000))

    return os.path.join(settings.MEDIA_ROOT, basedir, filename + ext)
