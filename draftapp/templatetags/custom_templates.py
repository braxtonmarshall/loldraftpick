from django import template

register = template.Library()


@register.simple_tag
def define(val=None):
    return val


@register.filter(is_safe=True)
def fix_champ(val=None):
    if val in ['KogMaw', 'RekSai']:
        return val
    elif val in ['Nunu&Willump']:
        return val[0:4]
    elif val in ['Wukong']:
        return 'MonkeyKing'
    else:
        return val.lower().capitalize()
