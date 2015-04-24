Changelog
=========

0.4.1
-----
#. Fix error in manifest.

0.4
---
#. Move javascript to a template so it can be customized.

0.3.3
-----
#. Change Django to django in setup.py.

0.3.2
-----
#. Republish slotRenderEnded event as DFPSlotRenderEnded.

0.3.1
-----
#. Allow targeting keys to be variables.

0.3
---
#. Deprecate `dfp_header`.
#. Allow arbitrary targeting keys and values to be passed to `{% dfp_tag %}` tag as key=value pairs.

0.2.2
-----
#. Scan for DFP div's with javascript. In practice this means DFP ads are now cacheable.

0.2.1
-----
#. Do not use enableSingleRequest method anymore since it destroys the ability to do subsequent DFP loads via ajax.

0.2
---
#. Async script loading has been re-added.
#. Deprecate the `dfp_header` tag and replace with `dfp_footer`. DFP will now work across all browsers.

0.1.2
-----
#. Remove async script loading since it does not work.

0.1.1
-----
#. Allow variables to be passed as arguments to the template tag.

0.1
---
#. First release.

