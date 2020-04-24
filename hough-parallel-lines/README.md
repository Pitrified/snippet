# Hough lines in a corridor

If the input data contains two *parallel* lines, and the distance between them is known
a priori, that information can be used to extract more information when analyzing each
point. A point can either be part of the left line, or the right one. During the
analysis, it is considered part of both. This way, two sinusoids are generated for each
point. There is no need to recompute the distances, because the distance from the right
line to the left is exactly the width of the corridor, so the values are just shifted.

```
       y
       |              l    r
       |             \    \       _
       |              \    \  _ -
       |               \  _ -
       |              _ .L   \
       |          _ -    \    \
       |       .-         \    \
       |      P
       o-----------------------> x

       y
       |         l    r
       |        \    \            _
       |         \    \       _ -
       |          \    \  _ -
       |           \  _ .L
       |          _ -    \
       |       .-    \    \
       |      P
       o-----------------------> x
```

The lines are represented by `theta`, the angle between the x axis and the `PT` segment.
Values of `theta` are in the range `[0, pi)`, and distances can be negative.

```
Note that l_rad is perpendicular to the line, and is the angle between the x
axis and PT. |PT| is |PL|*cos(TPL), and TPL = TPx - LPx = l_rad - PL_rad.

       y
       |   - _
       |       - _   T
       |           - _
       |             / - _ L
       |            /    . - _
       |           /   .       - _
       |          /  .
       |         / .
       |        /.
       |       .
       |      P
       o-----------------------> x

       y
       |
       |
       |                     L
       |                   _
       |               _ -.
       |           _ -  .
       |    T  _ -    .
       |   _ -      .
       |      \  .
       |       .
       |      P
       o-----------------------> x
```

