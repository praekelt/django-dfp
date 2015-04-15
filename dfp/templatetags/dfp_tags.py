from random import randint
from types import ListType, StringType

from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def dfp_footer(context):
    t = template.loader.get_template('dfp/dfp_footer.html')
    c = template.Context({})
    return t.render(c)


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
