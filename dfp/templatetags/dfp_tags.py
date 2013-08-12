from itertools import izip
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
    googletag.cmd.push(function() {

    var arr = document.getElementsByTagName('div');
    for (var i=0; i<arr.length; i++)
    {
        if (arr[i].className == 'gpt-ad')
        {
            var slot_name = arr[i].getAttribute('slot_name');
            var id = arr[i].getAttribute('id');
            var width = parseInt(arr[i].getAttribute('width'));
            var height = parseInt(arr[i].getAttribute('height'));

            googletag.defineSlot(slot_name, [width, height], id).addService(googletag.pubads());

            for (var attrs = 1; attrs <= arr[i].attributes.length; attrs++) {
                var key = arr[i].getAttribute('targeting_key' + attrs);
                if (key) {
                    var targeting_values = arr[i].getAttribute('targeting_values' + attrs).split("|");
                    googletag.pubads().setTargeting(key, targeting_values);
                }
            }
        }
    }

    // We can't use enableSingleRequest since that kills the ability to do
    // subsequent ajax loads that contain DFP tags. Someday DFP may provide a
    // disableSingleRequest method and then we can consider using it again.
    //googletag.pubads().enableSingleRequest();

    googletag.enableServices();

    var arr = document.getElementsByTagName('div');
    for (var i=0; i<arr.length; i++)
    {
        if (arr[i].className == 'gpt-ad')
        {
            var id = arr[i].getAttribute('id');
            googletag.cmd.push(function() { googletag.display(id); });
        }
    }

    });
</script>"""

    return result


@register.tag
def dfp_tag(parser, token):
    tokens = token.split_contents()[1:]
    if len(tokens) < 5:
        raise template.TemplateSyntaxError(
            'dfp tag requires arguments slot_name, width, height, targeting_key, targeting_value1, targeting_key2 targeting_value2, ...'
        )
    li = tokens[:3]
    pairs = tokens[3:]
    # this will drop unmatched key value pairs
    targeting = dict((key,val) for (key,val) in izip(pairs[::2],pairs[1::2]))
    li.append(targeting)
    return DfpTagNode(*li)


class DfpTagNode(template.Node):

    def __init__(self, slot_name, width, height, targeting):
        self.slot_name = template.Variable(slot_name)
        self.width = template.Variable(width)
        self.height = template.Variable(height)
        self.targeting = targeting

    def render(self, context):
        slot_name = self.slot_name.resolve(context)
        width = self.width.resolve(context)
        height = self.height.resolve(context)
        rand_id = randint(0, 2000000000)
        key_no = 1
        targeting = []
        for key, val in self.targeting.iteritems():
            try:
                key = template.Variable(key)
                val = template.Variable(val)
                key = key.resolve(context)
                vals = []
                val = val.resolve(context)
                if isinstance(val, ListType):
                    vals.extend(val)
                else:
                    vals.append(val)
                vals = '|'.join(vals)
                tags = 'targeting_key%d="%s"' % (key_no, key)
                tags += ' targeting_values%d="%s"' % (key_no, vals)
                targeting.append(tags)
            except template.VariableDoesNotExist:
                # if we can't resolve the var, ignore the pair
                pass
            key_no += 1

        di = {
            'rand_id': rand_id,
            'slot_name': slot_name,
            'width': width,
            'height': height,
            'targeting': ' '.join(targeting)
        }


        return """
<div id="div-gpt-ad-%(rand_id)s" class="gpt-ad"
     style="width: %(width)dpx; height: %(height)dpx;"
     slot_name="%(slot_name)s"
     width="%(width)s"
     height="%(height)s"
     %(targeting)s
 >
</div>""" % di
