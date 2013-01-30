from random import randint

from django import template


register = template.Library()


@register.simple_tag
def dfp_header():
    result = """
<script type='text/javascript'>
var googletag = googletag || {};
googletag.cmd = googletag.cmd || [];
(function() {
var gads = document.createElement('script');
gads.async = true;
gads.type = 'text/javascript';
var useSSL = 'https:' == document.location.protocol;
gads.src = (useSSL ? 'https:' : 'http:') + 
'//www.googletagservices.com/tag/js/gpt.js';
var node = document.getElementsByTagName('script')[0];
node.parentNode.insertBefore(gads, node);
})();

googletag.cmd.push(function() {
    googletag.pubads().enableSingleRequest(); 
    googletag.enableServices();
});
</script>
    """
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
        self.slot_name = unicode(slot_name.strip("'\""))
        self.width = int(width)
        self.height = int(height)
        self.targeting_key = unicode(targeting_key.strip("'\""))
        self.targeting_values = [unicode(s.strip("'\"")) for s in targeting_values]

    def render(self, context):        
        rand_id = randint(0, 2000000000)
        di = {
            'rand_id': rand_id,            
            'slot_name': self.slot_name, 
            'width': self.width, 
            'height': self.height, 
            'targeting_key': self.targeting_key, 
            'targeting_values': ', '.join(['"'+v+'"' for v in self.targeting_values])
        }
        if not hasattr(context, '_django_dfp'):
            setattr(context, '_django_dfp', [])
        getattr(context, '_django_dfp').append(di)
        return """
<div id="div-gpt-ad-%(rand_id)s" style="width: %(width)dpx; height: %(height)dpx;">
    <script type='text/javascript'>
        googletag.defineSlot('%(slot_name)s', [%(width)d, %(height)d], 'div-gpt-ad-%(rand_id)s').addService(googletag.pubads()).setTargeting('%(targeting_key)s', [%(targeting_values)s]);
        googletag.cmd.push(function() { googletag.display('div-gpt-ad-%(rand_id)s'); });
    </script>
</div>""" % di
