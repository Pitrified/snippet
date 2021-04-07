# Docs

## [Driver](https://pkg.go.dev/github.com/golang/exp/shiny/driver#Main)

Main is called by the program's main function to run the graphical application.

It calls f on the Screen, possibly in a separate goroutine, as some OS-
specific libraries require being on 'the main thread'. It returns when f
returns.

## [Screen](https://pkg.go.dev/golang.org/x/exp/shiny/screen)

Package screen provides interfaces for portable two-dimensional graphics and
input events.

### [Buffer](https://pkg.go.dev/golang.org/x/exp/shiny/screen#Buffer)

To see a Buffer's contents on a screen, upload it to a Texture (and then
draw the Texture on a Window) or upload it directly to a Window.

### [Drawer](https://pkg.go.dev/golang.org/x/exp/shiny/screen#Drawer)

Drawer is something you can draw Textures on.

Draw is the most general purpose of this interface's methods. It supports
arbitrary affine transformations, such as translations, scales and
rotations.

Copy and Scale are more specific versions of Draw. The affected dst pixels
are an axis-aligned rectangle, quantized to the pixel grid. Copy copies
pixels in a 1:1 manner, Scale is more general. They have simpler parameters
than Draw, using ints instead of float64s.

When drawing on a Window, there will not be any visible effect until Publish
is called.

### [EventDeque](https://pkg.go.dev/golang.org/x/exp/shiny/screen#EventDeque)

EventDeque is an infinitely buffered double-ended queue of events.

### [Screen](https://pkg.go.dev/golang.org/x/exp/shiny/screen#Screen)

Screen creates Buffers, Textures and Windows.

### [Texture](https://pkg.go.dev/golang.org/x/exp/shiny/screen#Texture)

Texture is a pixel buffer, but not one that is directly accessible as a
[]byte. Conceptually, it could live on a GPU, in another process or even be
across a network, instead of on a CPU in this process.

Buffers can be uploaded to Textures, and Textures can be drawn on Windows.

When specifying a sub-Texture via Draw, a Texture's top-left pixel is always
(0, 0) in its own coordinate space.

### [Uploader](https://pkg.go.dev/golang.org/x/exp/shiny/screen#Uploader)

Uploader is something you can upload a Buffer to.

### [Window](https://pkg.go.dev/golang.org/x/exp/shiny/screen#Window)

Window is a top-level, double-buffered GUI window.

## Samples

Mostly inspired by
[iview](https://github.com/sbinet/iview).

The shiny pkg has some
[sample](https://github.com/golang/exp/tree/master/shiny/example)
app.
