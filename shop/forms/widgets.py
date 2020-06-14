from django.forms import widgets


class CheckboxInput(widgets.CheckboxInput):
    template_name = 'djng/forms/widgets/bootstrap3/checkbox.html'


class RadioSelect(widgets.RadioSelect):
    template_name = 'djng/forms/widgets/bootstrap3/radio.html'


class Select(widgets.Select):
    template_name = 'djng/forms/widgets/bootstrap3/select.html'
