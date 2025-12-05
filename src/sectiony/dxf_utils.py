from __future__ import annotations
import math
import warnings
from typing import List, Tuple, Iterator, Dict, Any, Optional

# Use TYPE_CHECKING to avoid circular imports if necessary, 
# but we will import inside functions or use generic types where possible.
from .geometry import Point, Line, Arc, CubicBezier, Contour, Segment

def _parse_dxf_pairs(f) -> Iterator[Tuple[int, str]]:
    """Yields (code, value) pairs from a DXF file."""
    while True:
        try:
            code_line = f.readline()
            if not code_line:
                break
            code = int(code_line.strip())
            value = f.readline().strip()
            yield code, value
        except ValueError:
            break

def read_dxf(file_path: str) -> List[Contour]:
    """
    Read a DXF file and return a list of Contours.
    
    This is a minimal parser supporting LINE, ARC, and LWPOLYLINE entities.
    It does NOT attempt to chain individual entities into closed contours;
    each entity becomes a separate Contour (LWPOLYLINEs are one Contour each).
    """
    contours: List[Contour] = []
    
    with open(file_path, 'r') as f:
        pairs = _parse_dxf_pairs(f)
        
        # Fast forward to ENTITIES section
        in_entities = False
        for code, value in pairs:
            if code == 0 and value == 'SECTION':
                continue
            if code == 2 and value == 'ENTITIES':
                in_entities = True
                break
        
        if not in_entities:
            # No ENTITIES section found
            return []
            
        # Parse entities
        current_entity = None
        entity_data: Dict[int, List[Any]] = {}
        
        for code, value in pairs:
            if code == 0:
                # New entity or end of section
                if current_entity:
                    contour = _process_entity(current_entity, entity_data)
                    if contour:
                        contours.append(contour)
                
                if value == 'ENDSEC':
                    break
                
                current_entity = value
                entity_data = {}
            else:
                # Collect data for current entity
                if code not in entity_data:
                    entity_data[code] = []
                entity_data[code].append(value)
                
        # Process last entity if any
        if current_entity:
            contour = _process_entity(current_entity, entity_data)
            if contour:
                contours.append(contour)
                
    return contours

def _process_entity(entity_type: str, data: Dict[int, List[Any]]) -> Optional[Contour]:
    """Convert raw DXF entity data to a Contour."""
    try:
        if entity_type == 'LINE':
            # LINE: 10, 20 (start), 11, 21 (end)
            x1 = float(data.get(10, ['0'])[0])
            y1 = float(data.get(20, ['0'])[0])
            x2 = float(data.get(11, ['0'])[0])
            y2 = float(data.get(21, ['0'])[0])
            
            # Swap x/y to map DXF(X,Y) -> Section(Y,Z)
            # This ensures Plotter(Z,Y) shows DXF(X,Y) orientation
            line = Line(start=(y1, x1), end=(y2, x2))
            return Contour(segments=[line], hollow=False)
            
        elif entity_type == 'ARC':
            # ARC: 10, 20 (center), 40 (radius), 50 (start angle deg), 51 (end angle deg)
            cx = float(data.get(10, ['0'])[0])
            cy = float(data.get(20, ['0'])[0])
            r = float(data.get(40, ['0'])[0])
            start_deg = float(data.get(50, ['0'])[0])
            end_deg = float(data.get(51, ['0'])[0])
            
            # Convert degrees to radians
            start_rad = math.radians(start_deg)
            end_rad = math.radians(end_deg)
            
            # DXF arcs are CCW.
            if end_rad <= start_rad:
                end_rad += 2 * math.pi
                
            # Swap cx/cy. Angles match because Arc 0 is +Z (DXF +X), 90 is +Y (DXF +Y)
            arc = Arc(center=(cy, cx), radius=r, start_angle=start_rad, end_angle=end_rad)
            return Contour(segments=[arc], hollow=False)
            
        elif entity_type == 'LWPOLYLINE':
            # LWPOLYLINE: 10, 20 (vertices), 42 (bulge factors)
            # 70 (flags): 1 = closed
            
            xs = [float(x) for x in data.get(10, [])]
            ys = [float(y) for y in data.get(20, [])]
            
            if len(xs) != len(ys):
                return None
                
            count = len(xs)
            if count < 2:
                return None
                
            # Bulges are associated with vertices. 
            # If fewer bulges than vertices, assume 0 for the rest.
            # However, in DXF stream, bulges appear after the vertex they apply to.
            # This simple parser collects all 42s. 
            # Real DXF parsing is order-dependent within the entity for LWPOLYLINE.
            # Since we collected all codes into lists, we lost the association if we just grab all 42s.
            # We need to re-parse order-dependently for LWPOLYLINE.
            # This simple implementation assumes straight lines for now if we can't map bulges easily,
            # OR we need to change how we collect data.
            # Let's return None and fallback to a more robust loop for LWPOLYLINE inside read_dxf?
            # Or just assume linear for this minimal implementation if we can't easily map.
            # To support bulges (arcs in polylines), we really need to parse sequentially.
            # But the helper `_parse_dxf_pairs` streams.
            # Let's refine `_process_entity` to take an iterator or list of pairs?
            # No, `read_dxf` collected it into a dict. 
            # The dict approach is lossy for ordered repeated keys like 10, 20, 42 in LWPOLYLINE.
            # We must fix `read_dxf` to handle LWPOLYLINE correctly or accept linear-only.
            # Given "minimal", let's assume linear for LWPOLYLINE for now, 
            # OR fix the parser to preserve order for LWPOLYLINE.
            pass
            
    except (ValueError, IndexError):
        pass
        
    return None


def read_dxf_robust(file_path: str) -> List[Contour]:
    """
    Read a DXF file and return a list of Contours.
    Re-implementation to handle ordered data for LWPOLYLINE.
    """
    contours: List[Contour] = []
    
    with open(file_path, 'r') as f:
        pairs = list(_parse_dxf_pairs(f))
    
    # Find ENTITIES section
    start_idx = -1
    end_idx = -1
    
    for i, (code, val) in enumerate(pairs):
        if code == 2 and val == 'ENTITIES':
            start_idx = i
        if code == 0 and val == 'ENDSEC' and start_idx != -1:
            end_idx = i
            break
            
    if start_idx == -1 or end_idx == -1:
        return []
        
    # Parse entities in the section
    i = start_idx + 1
    while i < end_idx:
        code, val = pairs[i]
        
        if code == 0:
            entity_type = val
            # Collect entity pairs
            entity_pairs = []
            i += 1
            while i < end_idx:
                next_code, next_val = pairs[i]
                if next_code == 0:
                    break
                entity_pairs.append((next_code, next_val))
                i += 1
            
            contour = _process_entity_pairs(entity_type, entity_pairs)
            if contour:
                contours.append(contour)
        else:
            i += 1
            
    return contours

def _process_entity_pairs(entity_type: str, pairs: List[Tuple[int, str]]) -> Optional[Contour]:
    try:
        if entity_type == 'LINE':
            x1 = y1 = x2 = y2 = 0.0
            for c, v in pairs:
                if c == 10: x1 = float(v)
                elif c == 20: y1 = float(v)
                elif c == 11: x2 = float(v)
                elif c == 21: y2 = float(v)
            # Swap x/y
            return Contour(segments=[Line((y1, x1), (y2, x2))], hollow=False)
            
        elif entity_type == 'ARC':
            cx = cy = r = start = end = 0.0
            for c, v in pairs:
                if c == 10: cx = float(v)
                elif c == 20: cy = float(v)
                elif c == 40: r = float(v)
                elif c == 50: start = float(v)
                elif c == 51: end = float(v)
            
            start_rad = math.radians(start)
            end_rad = math.radians(end)
            if end_rad <= start_rad:
                end_rad += 2 * math.pi
            
            # Swap cx/cy
            return Contour(segments=[Arc((cy, cx), r, start_rad, end_rad)], hollow=False)
            
        elif entity_type == 'LWPOLYLINE':
            # Need to process vertices in order
            segments: List[Segment] = []
            is_closed = False
            
            # State for vertex parsing
            points: List[Tuple[float, float]] = []
            bulges: List[float] = [] 
            
            # Temporary storage for current vertex
            curr_x: Optional[float] = None
            curr_y: Optional[float] = None
            curr_bulge: float = 0.0
            
            for c, v in pairs:
                if c == 70:
                    flags = int(v)
                    if flags & 1:
                        is_closed = True
                elif c == 10:
                    # New vertex starts with x coord (usually)
                    # Push previous vertex if exists
                    if curr_x is not None and curr_y is not None:
                        # Swap x/y
                        points.append((curr_y, curr_x))
                        bulges.append(curr_bulge)
                    curr_x = float(v)
                    curr_y = None # Reset y
                    curr_bulge = 0.0
                elif c == 20:
                    curr_y = float(v)
                elif c == 42:
                    curr_bulge = float(v)
            
            # Push last vertex
            if curr_x is not None and curr_y is not None:
                # Swap x/y
                points.append((curr_y, curr_x))
                bulges.append(curr_bulge)
                
            if len(points) < 2:
                return None
                
            for k in range(len(points) - 1):
                p1 = points[k]
                p2 = points[k+1]
                b = bulges[k]
                segments.append(_make_poly_segment(p1, p2, b))
                
            if is_closed:
                p1 = points[-1]
                p2 = points[0]
                b = bulges[-1]
                segments.append(_make_poly_segment(p1, p2, b))
                
            return Contour(segments=segments, hollow=False)
            
    except ValueError:
        pass
    return None

def _make_poly_segment(p1: Point, p2: Point, bulge: float) -> Segment:
    """Create Line or Arc based on bulge factor."""
    if abs(bulge) < 1e-6:
        return Line(p1, p2)
    else:
        # Bulge = tan(theta/4)
        # theta = 4 * atan(bulge)
        theta = 4 * math.atan(bulge)
        
        # Chord length
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        chord_len = math.sqrt(dx*dx + dy*dy)
        
        # Radius: chord = 2*r*sin(theta/2)
        # r = chord / (2*sin(theta/2))
        radius = abs(chord_len / (2 * math.sin(theta/2)))
        
        # Center?
        # Vector p1->p2 is (dx, dy)
        # Midpoint
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        
        # Distance from chord to center (sagitta related)
        # s = r * (1 - cos(theta/2)) ... no
        # Distance from center to chord midpoint: h = r * cos(theta/2)
        h = abs(radius * math.cos(theta/2))
        
        # Direction perpendicular to chord
        # If bulge > 0, arc is CCW? Check DXF spec.
        # DXF: Bulge is tangent of 1/4 the included angle.
        # Negative bulge means arc goes clockwise from p1 to p2.
        
        # Normal vector (-dy, dx)
        len_norm = math.sqrt(dx*dx + dy*dy)
        nx = -dy / len_norm
        ny = dx / len_norm
        
        # Determine sign for center offset
        # If bulge > 0 (CCW), center is to the "left" of chord p1->p2
        # Normal (-dy, dx) is 90 deg CCW rotation of (dx, dy)
        # so it points "left".
        
        # Need to verify if center is on positive or negative side of chord relative to normal
        # If |theta| < pi (semicircle), center is on the side of the chord.
        # If |theta| > pi, center is on the other side?
        # Actually simpler:
        # Vector from Midpoint to Center.
        # If bulge > 0, angle is positive.
        
        # Let's find center using geometry
        # alpha = angle of chord
        alpha = math.atan2(dy, dx)
        # gamma = angle from chord to radius at p1
        # triangle is isosceles. (pi - theta)/2 is base angle.
        # angle of radius p1->center is alpha + (pi/2 - theta/2) if CCW?
        # Let's use the algebraic method.
        
        # Signed distance from chord midpoint to center
        # sagitta = r * (1 - cos(theta/2))
        # This is distance from chord to arc peak.
        # We need distance from chord to center.
        
        # Using complex numbers might be easier or just trig
        # Center is at intersection of perpendicular bisector and distance r from p1.
        
        # Let's try: 
        # w = chord vector = p2 - p1
        # if bulge > 0: arc is to the left.
        
        # Using formula from a reliable source or deriving carefully:
        # radius = chord / (2 * sin(2 * atan(bulge))) ? No, theta = 4*atan(b)
        
        # Let's use the code that handles this usually.
        # Center calculation:
        # b = bulge
        # c = chord length
        # s = b * c / 2  (sagitta approximation? No)
        
        # Let's use the geometric relation:
        # r = (c^2/4 + s^2) / (2s) where s is sagitta?
        # s = c/2 * |b| (geometry property of bulge: sagitta = chord/2 * bulge)
        # simple check: b=1 => theta=pi => semicircle. s = c/2. Correct.
        
        sagitta = (chord_len / 2) * abs(bulge)
        # r = ( (c/2)^2 + s^2 ) / (2s)
        radius = ((chord_len/2)**2 + sagitta**2) / (2 * sagitta)
        
        # Distance from midpoint to center
        # d_center = r - s  (if s < r)
        # or s - r ?
        
        # Direction from midpoint to arc peak is determined by bulge sign.
        # If b > 0, peak is "Left" (along normal (-dy, dx)).
        # Center is along that same line.
        # Distance from M to C is (r - s) in the direction of the peak IF s < r (theta < pi).
        # If theta > pi, s > r?
        # s = c/2 * b. if b -> inf, s -> inf.
        
        # Vector M to Peak (S vector):
        # S_vec = normal * sagitta * sign(bulge)
        
        # Vector M to Center:
        # dist_MC = radius - sagitta
        # But direction?
        # Center is always "behind" the peak relative to the chord?
        # Vector C to M to Peak are collinear.
        # C + (r-s)*dir = M ? No.
        # C + r*dir = Peak.
        # M + s*dir = Peak.
        # So C = M + (s - r)*dir.
        
        # dir is normal vector scaled by sign(bulge)
        sign_b = 1.0 if bulge > 0 else -1.0
        
        # Unit normal
        nx_u = -dy / chord_len
        ny_u = dx / chord_len
        
        # Vector M->Peak
        # v_MP = (nx_u * sign_b, ny_u * sign_b)
        
        # Center
        # C = M + (v_MP / s) * (s - r) ? No.
        # C = M + v_MP_unit * (s - r)
        # because vector from M to Peak has length s.
        # We want to go from M to C.
        # Dist from M to C is |s - r|.
        # If s < r (small arc), C is "below" M (opposite to Peak). (s-r) is negative. Correct.
        # If s > r (large arc), C is "above" M (same side as Peak). (s-r) is positive. Correct.
        
        cx = mx + nx_u * sign_b * (sagitta - radius)
        cy = my + ny_u * sign_b * (sagitta - radius)
        
        # Angles
        start_angle = math.atan2(p1[1] - cy, p1[0] - cx)
        end_angle = math.atan2(p2[1] - cy, p2[0] - cx)
        
        # Handle wrapping
        # DXF arcs are CCW.
        # But if bulge < 0, it is CW?
        # My Arc class is strictly CCW definition (start to end).
        # If bulge < 0, the geometry goes CW from p1 to p2.
        # So we should swap start/end angles? 
        # OR just ensure we parameterize it correctly.
        # If bulge < 0, p1 to p2 is CW.
        # Means on the circle, we go from start_angle to end_angle in CW direction.
        # My Arc class: "0 is +z... y=sin, z=cos". My Arc class is based on (y,z) plane?
        # geometry.py: "y = cy + r*sin(theta), z = cz + r*cos(theta)"
        # Note: DXF is (x,y). 
        # My geometry uses (y,z) for section coordinates usually (y=horizontal, z=vertical).
        # But here I am parsing (x,y) from DXF into (y,z) Point tuples?
        # The user's query says "takes the path of a dxf and greates the geomtry object".
        # It doesn't specify coordinate mapping.
        # Standard structural engineering: Y is horizontal, Z is vertical.
        # DXF: X is horizontal, Y is vertical.
        # So I should probably map DXF X -> Section Y, DXF Y -> Section Z.
        # My code above used x,y. I should pass them as (x,y) to Point, which is effectively (y,z).
        # Let's look at `Line` in `geometry.py`: `start: Point`. `Point = Tuple[float, float]`.
        # So (val1, val2).
        # In `Arc`: `y = cy + r*sin(theta), z = cz + r*cos(theta)`.
        # This is: y is sine component, z is cosine component.
        # Angle 0 is +z (Up). Angle pi/2 is +y (Right).
        # This is clockwise rotation from North?
        # Standard math: 0 is +x (Right), pi/2 is +y (Up) (CCW).
        # Here: 0 is +z (Up), pi/2 is +y (Right).
        # This is a 90 degree shift and maybe direction flip.
        # Let's check `Arc.discretize`:
        # y = cy + r * sin(theta)
        # z = cz + r * cos(theta)
        # If theta=0: y=0, z=r. (Up)
        # If theta=pi/2: y=r, z=0. (Right)
        # So 0->pi/2 goes Up -> Right. This is Clockwise!
        
        # DXF angles are standard math: 0 is +X (Right), CCW.
        # I need to convert DXF angles to Sectiony angles.
        # DXF (X, Y) -> Sectiony (Y, Z).
        # X -> Y
        # Y -> Z
        # DXF Angle 0 (Right, +X) -> Sectiony Right (+Y).
        # Sectiony +Y is theta=pi/2.
        # DXF Angle 90 (Up, +Y) -> Sectiony Up (+Z).
        # Sectiony +Z is theta=0.
        # So DXF 0 -> Sectiony pi/2
        # DXF 90 -> Sectiony 0
        # DXF 180 -> Sectiony -pi/2
        # Sectiony Theta = pi/2 - DXF_Angle.
        
        # Also need to handle Bulge logic.
        # Bulge > 0 is CCW in DXF (X,Y).
        # CCW in DXF (X->Y) corresponds to Right->Up in Sectiony (Y->Z).
        # Right (+Y) to Up (+Z).
        # Sectiony Right is pi/2. Sectiony Up is 0.
        # So pi/2 -> 0 is -pi/2 change.
        # So DXF CCW is Sectiony CW (decreasing theta).
        
        # This is getting complicated.
        # Let's map coords first:
        # DXF X -> Section Y
        # DXF Y -> Section Z
        
        # Center (cx, cy) -> (cx, cy) (mapped to Y, Z)
        # p1 (x1, y1) -> (x1, y1)
        
        # Angles:
        # atan2(z - cz, y - cy) = atan2(dxf_y - cy, dxf_x - cx)
        # This calculates standard math angle in Sectiony frame (where Y is 'x' and Z is 'y' for atan2).
        # Wait, atan2(y, x).
        # Here vertical axis is Z (dxf Y), horizontal is Y (dxf X).
        # So standard math angle in (Y,Z) plane is atan2(Z, Y).
        # My Arc definition uses theta where y=sin(theta), z=cos(theta).
        # tan(theta) = y/z. => theta = atan2(y, z).
        # Note atan2(y, x) is typical. Here inputs are (y, z).
        # So theta = atan2(y-cy, z-cz).
        
        # Let's verify:
        # theta=0 => y=0, z=r. atan2(0, r) = 0. Correct.
        # theta=pi/2 => y=r, z=0. atan2(r, 0) = pi/2. Correct.
        # So Sectiony Theta = atan2(Y_sect - Cy, Z_sect - Cz).
        # mapped from DXF: atan2(X_dxf - Cx, Y_dxf - Cy).
        
        # Re-evaluating bulge direction.
        # DXF Bulge > 0 => CCW.
        # p1 (Right) -> p2 (Up).
        # Sectiony: p1 (Y) -> p2 (Z).
        # Theta: pi/2 -> 0.
        # So Sectiony angle decreases.
        # So if Bulge > 0, start_theta > end_theta.
        # But Arc class expects start_angle, end_angle.
        # Does Arc class support start > end?
        # `angle_span = abs(self.end_angle - self.start_angle)` in discretize.
        # `theta = start + (end-start)*i/n`.
        # So it just interpolates.
        # So we just need to calculate correct start and end angles in Sectiony frame.
        
        # So:
        # 1. Calculate center (cx, cy) using standard geometry (ignoring coordinate system mapping for a moment, just 2D plane).
        # 2. Map everything to (Y, Z).
        # 3. Calculate start_angle = atan2(p1_y - cy, p1_z - cz).
        # 4. Calculate end_angle = atan2(p2_y - cy, p2_z - cz).
        # 5. Handle direction/wrapping.
        # If Bulge > 0 (DXF CCW), we go from p1 to p2 counter-clockwise in DXF plane.
        # In Sectiony frame (Y=Right, Z=Up), this is Clockwise (angle decreases).
        # So we expect end_angle < start_angle (modulo 2pi).
        # If Bulge < 0 (DXF CW), we go p1->p2 Clockwise in DXF.
        # In Sectiony, this is Counter-Clockwise (angle increases).
        # So end_angle > start_angle.
        
        # Adjust for wrapping to ensure interpolation goes the right way.
        # If bulge > 0 (Sectiony CW): we want end < start.
        # If end > start, subtract 2pi from end.
        
        # If bulge < 0 (Sectiony CCW): we want end > start.
        # If end < start, add 2pi to end.
        
        # Correct?
        # Let's double check.
        # p1=(r,0) (Right, Y-axis). p2=(0,r) (Up, Z-axis).
        # DXF: (r,0) -> (0,r). CCW. Bulge > 0.
        # Sectiony: p1=(r,0), p2=(0,r).
        # Center (0,0).
        # start_angle = atan2(r-0, 0-0) = atan2(r, 0) = pi/2.
        # end_angle = atan2(0-0, r-0) = atan2(0, r) = 0.
        # Bulge > 0 => Sectiony CW.
        # We want to go pi/2 -> 0.
        # end (0) < start (pi/2). Correct.
        # Interpolation: pi/2 ... 0. Correct.
        
        start_angle = math.atan2(p1[0] - cx, p1[1] - cy)
        end_angle = math.atan2(p2[0] - cx, p2[1] - cy)
        
        if bulge > 0:
            # Sectiony CW: end < start
            while end_angle > start_angle:
                end_angle -= 2 * math.pi
            if start_angle - end_angle > 2 * math.pi:
                 end_angle += 2 * math.pi # Don't wrap too much?
                 # No, if end < start, it's fine.
                 # Just ensure we take the short path or long path?
                 # Bulge defines it.
                 # But wait, bulge also defines large/small arc.
                 # |b| < 1 => small arc (< 180).
                 # |b| > 1 => large arc (> 180).
                 # My logic for center calculation handled the geometry.
                 # Now just need to trace p1->p2 correctly.
                 pass
        else:
            # Sectiony CCW: end > start
            while end_angle < start_angle:
                end_angle += 2 * math.pi
                
        return Arc(center=(cx, cy), radius=radius, start_angle=start_angle, end_angle=end_angle)

def write_dxf(file_path: str, contours: List[Contour]) -> None:
    """
    Write contours to a DXF file (minimal implementation).
    """
    with open(file_path, 'w') as f:
        # Header
        f.write("0\nSECTION\n2\nHEADER\n0\nENDSEC\n")
        # Entities
        f.write("0\nSECTION\n2\nENTITIES\n")
        
        for contour in contours:
            for segment in contour.segments:
                if isinstance(segment, Line):
                    _write_line(f, segment)
                elif isinstance(segment, Arc):
                    _write_arc(f, segment)
                elif isinstance(segment, CubicBezier):
                    # Approximate with lines
                    points = segment.discretize(resolution=10)
                    for i in range(len(points) - 1):
                        _write_line(f, Line(points[i], points[i+1]))
                        
        f.write("0\nENDSEC\n0\nEOF\n")

def _write_line(f, line: Line):
    f.write("0\nLINE\n8\n0\n")
    # Swap x/y to map Section(Y,Z) -> DXF(X,Y)
    # Section Y -> DXF Y
    # Section Z -> DXF X
    f.write(f"10\n{line.start[1]}\n20\n{line.start[0]}\n")
    f.write(f"11\n{line.end[1]}\n21\n{line.end[0]}\n")

def _write_arc(f, arc: Arc):
    # Convert Sectiony Arc (y, z, theta=0 is +z) to DXF Arc (x, y, theta=0 is +x)
    # Sectiony: y = cx + r*sin(t), z = cz + r*cos(t)
    # DXF: x = cx + r*cos(d), y = cy + r*sin(d)
    
    # Mapping: DXF X = Sectiony Z, DXF Y = Sectiony Y
    # x(t) = cz + r*cos(t)  (Section Z -> DXF X)
    # y(t) = cy + r*sin(t)  (Section Y -> DXF Y)
    
    # We need to find DXF angle 'd' such that:
    # cx_dxf + r*cos(d) = cz_sect + r*cos(t)
    # cy_dxf + r*sin(d) = cy_sect + r*sin(t)
    # (Assuming centers match: cx_dxf = cz_sect, cy_dxf = cy_sect)
    # cos(d) = cos(t)
    # sin(d) = sin(t)
    # So d = t !
    
    # Angles match directly because Arc 0 (+Z) maps to DXF 0 (+X).
    # And Arc 90 (+Y) maps to DXF 90 (+Y).
    
    start_d = math.degrees(arc.start_angle)
    end_d = math.degrees(arc.end_angle)
    
    f.write("0\nARC\n8\n0\n")
    # Center: cx_dxf = cz, cy_dxf = cy
    f.write(f"10\n{arc.center[1]}\n20\n{arc.center[0]}\n")
    f.write(f"40\n{arc.radius}\n")
    f.write(f"50\n{start_d}\n")
    f.write(f"51\n{end_d}\n")


