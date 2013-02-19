from random import randint
from types import ListType
import warnings

from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def dfp_header(context):
    warnings.warn("""Please migrate your templates to include {% dfp_footer %} \
near the end of the document body. dfp_header is marked for deprecation.""")
    secure = context['request'].is_secure() and 's' or ''
    result = """    
<script type="text/javascript" src="http%s://www.googletagservices.com/tag/js/gpt.js"></script>
<script type="text/javascript">
googletag.cmd.push(function() {
    googletag.pubads().enableSingleRequest(); 
    googletag.enableServices();
});
</script>
    """ % secure
    return result

@register.simple_tag(takes_context=True)
def dfp_footer(context):
    result = """
<script type="text/javascript">
    var googletag = googletag || {};
    googletag.cmd = googletag.cmd || [];
    (function() {
        var gads = document.createElement("script");
        gads.async = true;
        gads.type = "text/javascript";
        var useSSL = "https:" == document.location.protocol;
        gads.src = (useSSL ? "https:" : "http:") + "//www.googletagservices.com/tag/js/gpt.js";
        var node =document.getElementsByTagName("script")[0];
        node.parentNode.insertBefore(gads, node);
    })();
</script>

<script type="text/javascript">
    googletag.cmd.push(function() {"""

    for di in getattr(context['request'], '_django_dfp', []):
        result += """googletag.defineSlot('%(slot_name)s', [%(width)d, %(height)d], 'div-gpt-ad-%(rand_id)s').addService(googletag.pubads()).setTargeting('%(targeting_key)s', [%(targeting_values)s]);
""" % di

    result += """
googletag.pubads().enableSingleRequest(); 
googletag.enableServices();"""

    for di in getattr(context['request'], '_django_dfp', []):
        result += """googletag.cmd.push(function() { googletag.display('div-gpt-ad-%(rand_id)s'); });
""" % di

    result += """
    });
</script>"""

    return result


@register.tag
def dfp_tag(parser, token):
    tokens = token.split_contents()[1:]
    if len(tokens) < 5:
        raise template.TemplateSyntaxError(
            'menu tag requires arguments slot_name, width, height, targeting_key, targeting_value1, targeting_value2, ...'
        )
    li = tokens[:4]
    li.append(tokens[4:])
    return DfpTagNode(*li)


class DfpTagNode(template.Node):

    def __init__(self, slot_name, width, height, targeting_key, targeting_values):
        self.slot_name = template.Variable(slot_name)
        self.width = template.Variable(width)
        self.height = template.Variable(height)
        self.targeting_key = template.Variable(targeting_key)
        self.targeting_values = []        
        for v in targeting_values:
            self.targeting_values.append(template.Variable(v))

    def render(self, context):        
        slot_name = self.slot_name.resolve(context)
        width = self.width.resolve(context)
        height = self.height.resolve(context)
        targeting_key = self.targeting_key.resolve(context)
        targeting_values = []
        for v in self.targeting_values:
            resolved = v.resolve(context)
            if isinstance(resolved, ListType):
                targeting_values.extend(resolved)
            else:
                targeting_values.append(resolved)
        rand_id = randint(0, 2000000000)
        di = {
            'rand_id': rand_id,            
            'slot_name': slot_name, 
            'width': width, 
            'height': height, 
            'targeting_key': targeting_key, 
            'targeting_values': ', '.join(['"'+v+'"' for v in targeting_values])
        }
        if not hasattr(context['request'], '_django_dfp'):
            setattr(context['request'], '_django_dfp', [])
        getattr(context['request'], '_django_dfp').append(di)
        return """
<div id="div-gpt-ad-%(rand_id)s" style="width: %(width)dpx; height: %(height)dpx;">
</div>""" % di
