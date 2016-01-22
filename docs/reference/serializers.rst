.. _serializers:

================
REST Serializers
================

God programming style for application is to strictly separate of *Models*, *Views* and
*Controllers*. In classic Django jargon, *Views* act as, what we normally would denote a controller.

Controllers can sometimes be found on the server and sometimes on the client. In **djangoSHOP**
a significant portion of the controller code is written in JavaScript in the form of Angular
directives_.

Therefore, all data exchange between the *View* and the *Model* must be performed in a serializable
format, namely JSON. This allows us to use the same business logic for the server, as well as for
the client. It also means, that we could create native mobile apps, which communicate with a
web-application, without ever seeing a line of HTML code.


Every URL is a REST endpoint
============================

