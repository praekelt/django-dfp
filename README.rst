Django DFP
==========
**App that provides tags to fetch Google DFP ads.**

.. contents:: Contents
    :depth: 5

Overview
--------

Google provides server side adds via its DFP service. This product is inspired
by the code at
http://support.google.com/dfp_sb/bin/answer.py?hl=en&answer=1651549. To keep
the Django implementation as simple as possible this product changes the order
of the Javascript from that page.

Installation
------------

#. Install or add ``django-dfp`` to your Python path.

#. Add ``dfp`` to your ``INSTALLED_APPS`` setting.

Usage
-----

Load `dfp_tags` in your template with `{% load dfp_tags %}`. Call `{ %dfp_footer %}`
once near the end of your document body. You would typically call it just
before the closing body tag.

An example tag is

    {% dfp_tag "/1234/travel" 300 250 interests="sports,music" position="top" color=variable foo=bar %}

String values are comma delimited. Note the lack of spaces around the comma.
Both keys and values can be variables.

You may call as many tags as you want. See http://support.google.com/dfp_sb/bin/answier.py?hl=en&answer=1651549 for more examples.

