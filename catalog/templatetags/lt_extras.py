from django import template

register = template.Library()


@register.filter
def cover_variant(value):
    """Map any string (e.g. ISBN or title) to one of 5 pastel cover styles."""
    if not value:
        return 1
    return (sum(ord(c) for c in str(value)) % 5) + 1


@register.filter
def initials(value):
    """First letters of the first two words — used for avatar chips."""
    parts = str(value).split()
    letters = "".join(p[0] for p in parts[:2])
    return letters.upper()


@register.filter
def lookup(mapping, key):
    """Get mapping[key] in a template, e.g. {{ borrow_status|lookup:inventory.id }}."""
    try:
        return mapping.get(key)
    except AttributeError:
        return None
