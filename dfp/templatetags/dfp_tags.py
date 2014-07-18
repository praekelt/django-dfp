from random import randint
from types import ListType, StringType

from django import template


register = template.Library()


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

    var stack = new Array();
    var reserved = ['slot_name', 'id', 'width', 'height', 'style', 'class'];
    var arr = document.getElementsByTagName('div');
    for (var i=0; i<arr.length; i++)
    {
        if (arr[i].className == 'gpt-ad')
        {
            var slot_name = arr[i].getAttribute('slot_name');
            var id = arr[i].getAttribute('id');
            var width = parseInt(arr[i].getAttribute('width'));
            var height = parseInt(arr[i].getAttribute('height'));
            var slot = googletag.defineSlot(slot_name, [width, height], id).addService(googletag.pubads());

            for (var j=0; j<arr[i].attributes.length; j++){
                var attr = arr[i].attributes[j];
                if (attr.name.indexOf('data-pair-') == 0){
                    var key = attr.name.slice(10);
                    var value = attr.value.split('|');
                    slot.setTargeting(key, value);
                }
            }
            stack.push(slot);
        }
    }

    // We can't use enableSingleRequest since that kills the ability to do
    // subsequent ajax loads that contain DFP tags. Someday DFP may provide a
    // disableSingleRequest method and then we can consider using it again.
    //googletag.pubads().enableSingleRequest();

    // Republish slotRenderEnded event because pubads disappears after
    // enableServices.
    googletag.pubads().addEventListener('slotRenderEnded', function(event){
        var evt = new CustomEvent('DFPSlotRenderEnded', {
            detail: {
                dfp_event: event
            }
        });
        document.dispatchEvent(evt);
    });

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

    /* Not ready yet - ajacx reloads
    (function where_am_i_worker(){
        googletag.pubads().refresh(stack);
        setTimeout(where_am_i_worker, 10000);
    })();
    */

    });
</script>"""

    return result


@register.tag
def dfp_tag(parser, token):
    tokens = token.split_contents()[1:]
    if len(tokens) < 4:
        raise template.TemplateSyntaxError(
            'dfp tag requires arguments slot_name width height targeting_key_1="targeting_value_11",..,"targeting_value_12" ...'
        )
    li = tokens[:3]
    keyvals = {}
    for l in tokens[3:]:
        k, v = l.split('=')
        keyvals[k] = v
    return DfpTagNode(*li, **keyvals)


class DfpTagNode(template.Node):

    def __init__(self, slot_name, width, height, **keyvals):
        self.slot_name = template.Variable(slot_name)
        self.width = template.Variable(width)
        self.height = template.Variable(height)
        self.keyvals = {}
        for k, v in keyvals.items():
            self.keyvals[template.Variable(k)] = template.Variable(v)

    def render(self, context):
        # Resolve values
        slot_name = self.slot_name.resolve(context)
        width = self.width.resolve(context)
        height = self.height.resolve(context)
        pairs = {}
        for k, v in self.keyvals.items():
            try:
                k_resolved = k.resolve(context)
            except template.VariableDoesNotExist:
                k_resolved = k
            try:
                v_resolved = v.resolve(context)
            except template.VariableDoesNotExist:
                continue
            if isinstance(v_resolved, StringType):
                v_resolved = v_resolved.split(',')
            elif not isinstance(v_resolved, ListType):
                v_resolved = [v_resolved]
            pairs[k_resolved] = v_resolved

        # Prepare tag
        rand_id = randint(0, 2000000000)
        di = {
            'rand_id': rand_id,
            'slot_name': slot_name,
            'width': width,
            'height': height
        }
        result = """
<div id="div-gpt-ad-%(rand_id)s" class="gpt-ad"
     style="width: %(width)dpx; height: %(height)dpx;"
     slot_name="%(slot_name)s"
     width="%(width)s"
     height="%(height)s"
""" % di

        # Append pairs
        for k, v in pairs.items():
            result += ' data-pair-%s="%s"' % (k, '|'.join(v))
        result += "></div>"

        return result
