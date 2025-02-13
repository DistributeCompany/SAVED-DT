from folium import Icon
from typing import Any

def create_custom_icon(
    icon: str = 'info-sign',
    color: str = 'blue',
    icon_color: str = 'white',
    prefix: str = 'fa'
) -> Icon:
    """
    Create a custom Folium Icon based on the provided parameters.

    Parameters
    ----------
    icon : str, optional
        The name of the icon (default is 'info-sign').
    color : str, optional
        The color of the marker (default is 'blue').
    icon_color : str, optional
        The color of the icon (default is 'white').
    prefix : str, optional
        The prefix for the icon set (default is 'fa').

    Returns
    -------
    folium.Icon
        A customized Folium Icon object.


    """
    return Icon(icon=icon, color=color, icon_color=icon_color, prefix=prefix)