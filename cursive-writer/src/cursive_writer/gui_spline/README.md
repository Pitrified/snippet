# Spline drawing GUI

### TODO

* File dialog to save glyphs
* Rescale from abs (image) to normalized (FM coord)
* Add buttons to change selected SP data, left, very left, orientation
* Add loading of a glyph, after FMlines are set, remap those points to the current image
* Make the point list scroll when adding points if it is filled
* Move spline buttons and info to left sidebar
* `line_curve_point` is called with swapped args sometimes, check that

### MAYBE

* Is there really a reason to put FrameInfo as a different class? It could just be a regular frame inside the view.

##### Done

* Make scrollable the point frame list
* When hovering a FrameSPoint, turn the correspondent arrow a different color
* When clicking a FrameSPoint, set that as selectedSP
* Button to delete FSP in the spline info pane
* If deleting when a header is selected, merge the two glyphs before/after that
* After deleting a point set as selected the previous one, if it is the first select the spline header

### Ideas

* Each spline point has unique ID, the splines are list of IDs

### On logging

* You can artificially _lower_ the loglevel inside a function to debug that, but in regular use you should not change it: that way it is controlled easily at app level.
* I should try to change a level for an entire class and see if it works as I expect
