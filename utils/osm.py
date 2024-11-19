import folium 

def create_custom_icon(icon='info-sign', color='blue', icon_color='white', prefix='fa'):
    """
    Create a Folium Icon based on input parameters.

    Parameters:
    - icon (str): The name of the icon.
    - color (str): The color of the marker. Default is 'blue'.
    - icon_color (str): The color of the icon. Default is 'white'.
    - prefix (str): The prefix for the icon set. Default is 'fa'.

    Returns:
    - folium.Icon: The customized Folium icon object.
    """
    return folium.Icon(icon=icon, color=color, icon_color=icon_color, prefix=prefix)