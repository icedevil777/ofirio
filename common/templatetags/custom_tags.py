from django import template


register = template.Library()


class FrontColors:
    """Colors used on front end"""
    red = '#ef4b44'
    orange = '#ff9900'
    green = '#01d092'


@register.filter
def mult(value, arg):
    """Multiply the arg and the value"""
    return float(value) * float(arg)


@register.filter
def subt(value, arg):
    """Subtract the arg from the value"""
    return value - arg


@register.filter
def is_dict(obj):
    """This approach detects all kinds of dict-like object"""
    try:
        dict(obj)
        return True
    except Exception:
        return False


@register.filter
def is_deep(dikt):
    """Return True if any value is a dict"""
    for value in dikt.values():
        if is_dict(value):
            return True
    return False


@register.filter
def keyvalue(dikt, key):
    try:
        return dikt[key]
    except Exception:
        return ''


@register.filter
def times(number):
    """To use as a range in for loops"""
    return range(number)


@register.filter
def front_color_cap_coc(value):
    """
    Repeat logic from
    portal-front/src/components/helpers/colorSchemes.ts
    cap-coc() function
    """
    if value < 0:
        color = FrontColors.red
    elif value <= 0.02:
        color = ''
    elif value <= 0.05:
        color = FrontColors.orange
    else:
        color = FrontColors.green
    return color


@register.filter
def front_color_ten_point_rating(value):
    """
    Repeat logic from
    portal-front/src/components/helpers/colorSchemes.ts
    tenPointRating() function
    """
    value = value or 5
    if value < 3:
        color = FrontColors.red
    elif value >= 8:
        color = FrontColors.green
    else:
        color = ''
    return color


@register.filter
def front_color_pos_neg(value):
    """
    Repeat logic from
    portal-front/src/components/helpers/colorSchemes.ts
    posNeg() function
    """
    if value < 0:
        return FrontColors.red
    elif value > 0:
        return FrontColors.green
    return ''


@register.simple_tag
def setvar(val=None):
    """Legacy. Don't use it"""
    return val


@register.simple_tag
def define(var):
    """Legacy. Don't use it"""
    global somevariable
    somevariable = var
    return somevariable
