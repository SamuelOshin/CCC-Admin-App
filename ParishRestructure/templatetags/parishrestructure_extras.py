from django import template
from ParishRestructure.models import Location

register = template.Library()

@register.simple_tag
def get_all_locations():
    """
    Template tag to get all locations ordered by level and name.
    Returns all locations for use in location selection dropdowns.
    """
    return Location.objects.all().order_by('level', 'name')

@register.simple_tag
def get_locations_by_level(level):
    """
    Template tag to get locations filtered by level.
    
    Args:
        level (str): The location level to filter by
        
    Returns:
        QuerySet: Filtered locations
    """
    return Location.objects.filter(level=level).order_by('name')
