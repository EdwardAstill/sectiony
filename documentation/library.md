# Standard Library Shapes

The `sectiony.library` module provides functions to easily generate common structural sections.

## Circular Hollow Section (chs)
`chs(d, t)`

*   **d**: Outer diameter
*   **t**: Wall thickness

## Rectangular Hollow Section (rhs)
`rhs(b, h, t, r)`

*   **b**: Width (z-direction)
*   **h**: Height (y-direction)
*   **t**: Wall thickness
*   **r**: Outer corner radius

## I Section (i)
`i(d, b, tf, tw, r)`

*   **d**: Depth (Height, y-direction)
*   **b**: Width (Base, z-direction)
*   **tf**: Flange thickness
*   **tw**: Web thickness
*   **r**: Root radius (fillet between web and flange)

## U (Channel) Section (u)
`u(b, h, t, r)`

*   **b**: Width (z-direction)
*   **h**: Height (y-direction)
*   **t**: Thickness (uniform for web and flanges)
*   **r**: Outside corner radius

*Note: The `n` parameter (number of segments) mentioned in older documentation is no longer required as the library now uses native curve representations (`Arc`) which are discretized automatically based on resolution.*
