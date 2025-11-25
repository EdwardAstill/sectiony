import math
from typing import List, Tuple

def arc(center_y: float, center_z: float, radius: float, start_angle: float, end_angle: float, n: int) -> List[Tuple[float, float]]:
    """
    Generate points for an arc in (y, z) coordinates.
    y is Vertical (Up), z is Horizontal (Right).
    Angles in radians, 0 is +z (Right), pi/2 is +y (Up).
    
    Args:
        center_y: Y-coordinate of center
        center_z: Z-coordinate of center
        radius: Arc radius
        start_angle: Starting angle in radians
        end_angle: Ending angle in radians
        n: Number of segments
        
    Returns:
        List of (y, z) tuples
    """
    points = []
    # If radius is tiny, just return center
    if radius <= 1e-9:
        return [(center_y, center_z)]

    if n < 1: n = 1
        
    for i in range(n + 1):
        theta = start_angle + (end_angle - start_angle) * i / n
        # y = R sin(theta), z = R cos(theta)
        y = center_y + radius * math.sin(theta)
        z = center_z + radius * math.cos(theta)
        points.append((y, z))
    return points
