# App structure experiments

## Sidebar

Rotate is pretty neat, but there are problems with the binding.

### Controller ?

* click a button to `move` by `10`
* in the callback specific for the button, call `controller.move(10)`
* the controller calls the right function `model.move(10)`
* the model does the thing, and changes its state `model.x`
    (in a way that could be extremely complex)
* the controller waits for the end of the update
* the controller calls `view.updatePos(model.x)`
* `view.updatePos` know all the widget that must be changed to show the new `x` value

The point is that the view must not keep track of the state,
cannot have a parallel `view.x` field

The binding would be easy to use: bind `view.xBind` to `model.x`
and when `model.x` changes, `view.xBind` tells all the widgets to change
(because you registered the widgets and the bind, so it's basically an Observable).
This is too powerful tho, the bind must not be able to change the model state.

The need for `Observable`s arises from the fact that
the model could change a lot more fields than just `x`.
So we register `y` as observable with a proper callback
and if the model changes that field we don't need to do anything,
the callback is already there to react and update the view.

### Animation ?

On top of that consideration,
remember that we would like to keep the thing async and passively animate.

It is silly to re-draw everything with a refresh, reading all the state of the model.

```go
case <-tickRefresh.C:
case <-tickSimulate.C:
```

This are completely different objectives.

Anyway, `animate` is basically a controller (?):
the `simulate` side changes the `model` state,
the `refresh` side changes the `view` to reflect the current state.

In `fynesample/image/image4/imagesample.go`
we fell in the pitfall of having the model and the view in the same struct:

```go
case <-tickRefresh.C:
    a.aRaster.Refresh()
case <-tickSimulate.C:
    a.aRaster.backColor += 1
    if a.aRaster.backColor > 200 { a.aRaster.backColor = 40 }
```

so there is no separation at all between the two.
