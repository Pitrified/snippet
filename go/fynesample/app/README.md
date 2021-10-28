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

### MVC

The view does not implement any logic.

If the folder changes in the model,
the view will update the relative label and that's it.
It is the model that will read the content of the new folder
and update the file list.
The view will be notified of this second change, and will reflect it.

We use the observable behavior, with data binding:
the model does not need to use the `Observable` type,
we link instead a binding to the regular field in the model.
When the field changes,
the binding will magically know that,
and the proper callback will be fired.

No magic (duh):
a call to `data.Reload()` is needed
to notify the data binding that the value has changed,
so we still need to modify the model.

Or at least we need a *very* smart controller,
that knows all the side effect caused by a function.
But this looks very brittle:
if I call `move(0)`, the values of `x` and `y` will not change,
and it is wasteful calling `xData.reload()` every time
(e.g. instead of a simple label this could need a redraw of an entire image).

With the binding, some widget might even be updated automatically
(e.g. a simple label), without a callback that sets the new text in the label.

I don't like the two-way data binding.

> Complete data binding (two-way or bidirectional) ensures that as well as
> keeping presented data up to date, it will also update the source data if the
> user alters the presentation through some interactive widget.

[Building Cross-Platform GUI Applications with Fyne](https://books.google.it/books?id=oV0XEAAAQBAJ&pg=PA164&lpg=PA164&dq=Complete+data+binding+(two-way+or+bidirectional)+ensures+that+as+well+as+keeping+presented+data+up+to+date,+it+will+also+update+the+source+data+if+the+user+alters+the+presentation+through+some+interactive+widget.&source=bl&ots=QKGmGc3J5C&sig=ACfU3U3rFDZGCxgufsFbTE0uialw04jEPw&hl=en&sa=X&ved=2ahUKEwjxxc-T1ezzAhUSt6QKHXscCekQ6AF6BAgCEAM#v=onepage&q=Complete%20data%20binding%20(two-way%20or%20bidirectional)%20ensures%20that%20as%20well%20as%20keeping%20presented%20data%20up%20to%20date%2C%20it%20will%20also%20update%20the%20source%20data%20if%20the%20user%20alters%20the%20presentation%20through%20some%20interactive%20widget.&f=false)

This is what is strange for me:
if a slider changes the zoom level,
updating the label is not enough:
you need to compute the new image and update that.
