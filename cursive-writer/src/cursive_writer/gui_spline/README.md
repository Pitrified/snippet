# Spline drawing GUI

### TODO

* The letters are drawn with thickness 10: when joining two glyphs at 90 deg angle with a different thickness, it does not look good. Fix it.
* Control things with keyboard
* Add loading of a glyph, after FMlines are set, remap those points to the current image
* Make the point list scroll when adding points if it is filled
* GUI to build splines by assembling glyphs

### MAYBE

* Is there really a reason to put FrameInfo as a different class? It could just be a regular frame inside the view.
* Move spline buttons and info to left sidebar

##### Done

* Make scrollable the point frame list
* When hovering a FrameSPoint, turn the correspondent arrow a different color
* When clicking a FrameSPoint, set that as selectedSP
* Button to delete FSP in the spline info pane
* If deleting when a header is selected, merge the two glyphs before/after that
* After deleting a point set as selected the previous one, if it is the first select the spline header
* Rescale from abs (image) to normalized (FM coord)
* Add buttons to change selected SP data, left, very left, orientation
* File dialog to save glyphs
* Do not draw segments between glyphs, they are there for a reason
* Dark mode
* Set from CLI theme and thickness and loglevel

### Ideas

* Each spline point has unique ID, the splines are list of IDs
* For the ligatures: disregard the glyphs and look at the points orientation, chop off the letter wherever needed. Different version of a letter with different attach point are allowd (and needed).

### On logging

* You can artificially _lower_ the loglevel inside a function to debug that, but in regular use you should not change it: that way it is controlled easily at app level.
* I should try to change a level for an entire class and see if it works as I expect
