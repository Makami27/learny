from django import template

register = template.Library()

# Purely presentational grouping used to color-code subject badges/cards
# in the new design. Does not affect any booking/matching logic.
_SUBJECT_GROUPS = {
    'piano': 'music',
    'guitar': 'music',
    'violin': 'music',
    'voice': 'music',
    'math': 'academic',
    'reading': 'academic',
    'science': 'academic',
    'coding': 'academic',
    'art': 'art',
    'swimming': 'skills',
    'chess': 'skills',
    'dance': 'skills',
    'other': 'other',
}


@register.filter
def subject_group(subject_code):
    """Return a short design-group key ('music', 'academic', 'art',
    'skills', 'other') for a given SUBJECT_CHOICES code, used only to
    pick a badge/card accent color."""
    return _SUBJECT_GROUPS.get(subject_code, 'other')
