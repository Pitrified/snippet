# Spline drawing GUI

### TODO

* Add button to hide glyph in thick view
* When saving, skip empty glyphs
* Better support for blank image:
    * background color
    * autoset FM lines
* Use shift to align FM
* When moving glyphs, use shoft to move along axis
* Interactive moving of glyphs, redraw only the thin segment
* If a segment was only translated, there is no need to recompute everything, just,
  well, translate it
* When asking for file names, check in the controller if the action is allowed
  (`fm_lines_abs is not None`) before showing the prompt
* Move FM lines, click button to enter base/mean movement mode, then usual qwerasdf movement
* Duplicate glyph, add it a bit translated to show it
* Rotate glyph
* Rotate glyph 180
* Rotate point 180
* The letters are drawn with thickness 10: when joining two glyphs at 90 deg angle with
  a different thickness, it does not look good
* GUI to build splines by assembling glyphs
* Control more things with keyboard
* Make the point list scroll when adding points if it is filled
* `redraw_canvas` should be done in `move_image`, not in `release_click_canvas`, and
  similar cases
* Throttle keypress events, set a flag `active` and ignore other events? Why do they
  even get caled so frequently if they are bound to `KeyRelease`?
* Check if the FM lines are set before going to afjust fm lines state

### MAYBE

* The function names in `model` are slightly wrong: it should not be called
  `clicked_sh_btn_new_spline`, the model does not care what generated that. Call it
  `start_new_spline` (as a bonus misleading name, this should be called `new_glyph`). In
  the controller there is `clicked_sh_btn_new_spline`, that is correctly telling that this
  is a reaction to a button click, and in that function the controller will call
  `model.start_new_spline`.
* Is there really a reason to put FrameInfo as a different class? It could just be a regular frame inside the view.
* Move spline buttons and info to left sidebar, or some info to right sidebar.

##### Done

* Move glyph with mouse click
* Move glyph by selecting a point, then another, and translate the first over the second
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
* Create the file dialog in the view, inside the controller, ask for the destination, calling a method inside the view, that returns the path.
* When writing the root glyph name, the points move when pressing qwerasdfzxcv...
* Add loading of a glyph, after FMlines are set, remap those points to the current image
* Show the `adjust_base/mean` state by changing the background color of the label

### Ideas

* Each spline point has unique ID, the splines are list of IDs
* For the ligatures: disregard the glyphs and look at the points orientation, chop off the letter wherever needed. Different version of a letter with different left attach point (high/low) are needed.

### On logging

* You can artificially _lower_ the loglevel inside a function to debug that, but in regular use you should not change it: that way it is controlled easily at app level.
* I should try to change a level for an entire class and see if it works as I expect

### Errors

When clicking in the same spot twice thick segment update fails:

```
File "cursive-writer/src/cursive_writer/gui_spline/draw_controller.py", line 278, in released_canvas
   self.model.release_click_canvas(click_type, event.x, event.y)
File "cursive-writer/src/cursive_writer/gui_spline/draw_model.py", line 254, in release_click_canvas
   self.add_spline_point()
File "cursive-writer/src/cursive_writer/gui_spline/draw_model.py", line 936, in add_spline_point
   self.add_spline_abs_point(abs_op)
File "cursive-writer/src/cursive_writer/gui_spline/draw_model.py", line 966, in add_spline_abs_point
   self.update_thick_segments()
File "cursive-writer/src/cursive_writer/gui_spline/draw_model.py", line 1121, in update_thick_segments
   self.spline_thick_holder.update_data(all_fm, path)
File "cursive-writer/src/cursive_writer/utils/spline_segment_holder.py", line 88, in update_data
   self.cached_pos[spid0], new_all_SP[spid1],
File "cursive-writer/src/cursive_writer/utils/spline_segment_holder.py", line 114, in compute_segment_points
   x_segment, y_segment = compute_thick_spline(p0, p1, self.thickness)
File "cursive-writer/src/cursive_writer/spliner/spliner.py", line 416, in compute_thick_spline
   coeff_t = fit_cubic(p0t, p1t)
File "cursive-writer/src/cursive_writer/spliner/spliner.py", line 123, in fit_cubic
   x = np.linalg.solve(A, b)
File "<__array_function__ internals>", line 6, in solve
File "ckages/numpy/linalg/linalg.py", line 399, in solve
   r = gufunc(a, b, signature=signature, extobj=extobj)
File "ckages/numpy/linalg/linalg.py", line 97, in _raise_linalgerror_singular
   raise LinAlgError("Singular matrix")
numpy.linalg.LinAlgError: Singular matrix   
```

Ideas:

* Fix `fit_cubic`, hopefully thick will not fail with empty/small top contour (note that
  this failed in `coeff_t = fit_cubic(p0t, p1t)`

