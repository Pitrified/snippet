# TODOs

* Check which fill mode is better for the canvas.
* Max zoom level +10 from base
* Redrawing after each movement is too slow:
    rather than doing all points,
    the event put them in a special queue,
    if the size of the queue is too large,
    drop some intermediate points
* Use better filter to downscale the image, not `xdraw.NearestNeighbor`

# IDEAs

* Use a raster to show the image,
  the draw function just returns `subImage` properly rescaled.
