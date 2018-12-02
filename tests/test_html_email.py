import os
import pytest
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.mail.message import SafeMIMEMultipart, SafeMIMEText
from django.core.files.images import ImageFile
from django.template.loader import get_template
from html_email.template import render_to_string
from html_email.template.backends.html_email import EmailTemplates


def test_text():
    template = get_template('hello.html', using='html_email')
    assert isinstance(template.backend, EmailTemplates)
    context = {'foo': "Bar"}
    content = template.render(context)
    assert content == '<h1>Bar</h1>'


def test_html():
    template = get_template('image.html', using='html_email')
    body = template.render({'imgsrc': 'django-shop-logo.png'})
    assert body == """
<h3>Testing image attachments</h3>
<img src="cid:django-shop-logo.png" width="200" />
"""
    subject = "[django-SHOP unit tests] attached image"
    msg = EmailMultiAlternatives(subject, body, to=['jacob.rief@gmail.com'])
    template.attach_images(msg)
    msg.content_subtype = 'html'
    msg.mixed_subtype = 'related'
    # this message can be send by email
    parts = msg.message().walk()
    part = next(parts)
    assert isinstance(part, SafeMIMEMultipart)
    part = next(parts)
    assert isinstance(part, SafeMIMEText)
    assert part.get_payload() == body
    part = next(parts)
    assert isinstance(part, MIMEImage)
    assert part.get_content_type() == 'image/png'
    assert part.get_content_disposition() == 'inline'
    assert part.get_filename() == 'django-shop-logo.png'
    assert part['Content-ID'] == '<django-shop-logo.png>'

    #connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
    #connection.send_messages([msg])


def test_mixed():
    body = "Testing mixed text and html attachments"
    html, attached_images = render_to_string('image.html', {'imgsrc': 'django-shop-logo.png'}, using='html_email')
    subject = "[django-SHOP unit tests] attached image"
    msg = EmailMultiAlternatives(subject, body, to=['jacob.rief@gmail.com'])
    msg.attach_alternative(html, 'text/html')
    for attachment in attached_images:
        msg.attach(attachment)
    msg.mixed_subtype = 'related'
    # this message can be send by email
    parts = msg.message().walk()
    part = next(parts)
    assert isinstance(part, SafeMIMEMultipart)
    part = next(parts)
    assert isinstance(part, SafeMIMEMultipart)
    part = next(parts)
    assert isinstance(part, SafeMIMEText)
    assert part.get_content_type() == 'text/plain'
    assert part.get_payload() == body
    part = next(parts)
    assert isinstance(part, SafeMIMEText)
    assert part.get_content_type() == 'text/html'
    assert part.get_payload() == html
    part = next(parts)
    assert isinstance(part, MIMEImage)
    assert part.get_content_type() == 'image/png'

    #connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
    #connection.send_messages([msg])


def test_image():
    relfilename = 'static/django-shop-logo.png'
    filename = os.path.join(os.path.dirname(__file__), relfilename)
    logo = ImageFile(open(filename, 'rb'), name=relfilename)
    template = get_template('image.html', using='html_email')
    body = template.render({'imgsrc': logo})
    assert body == """
<h3>Testing image attachments</h3>
<img src="cid:static/django-shop-logo.png" width="200" />
"""
    subject = "[django-SHOP unit tests] attached image"
    msg = EmailMultiAlternatives(subject, body, to=['jacob.rief@gmail.com'])
    template.attach_images(msg)
    # this message can be send by email
    parts = msg.message().walk()
    part = next(parts)
    assert isinstance(part, SafeMIMEMultipart)
    part = next(parts)
    assert isinstance(part, SafeMIMEText)
    assert part.get_payload() == body
    part = next(parts)
    assert isinstance(part, MIMEImage)
    assert part.get_content_type() == 'image/png'
    assert part.get_content_disposition() == 'inline'
    assert part.get_filename() == relfilename
    assert part['Content-ID'] == '<{}>'.format(relfilename)
