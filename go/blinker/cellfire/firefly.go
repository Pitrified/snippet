package cellfire

import "fmt"

// Firefly represents a firefly in the environment.
type Firefly struct {
	X, Y float32 // Position on the map.
	O    int16   // Orientation in half degrees: O=3 means Deg=6.

	id int // Unique id of the firefly.

	c *Cell  // Cell currently occupied.
	w *World // World this firefly is in.
}

// Create a new firefly.
func NewFirefly(x, y float32, o int16, id int, c *Cell, w *World) *Firefly {
	// create the firefly
	f := &Firefly{x, y, o, id, c, w}
	w.chChangeCell <- &ChangeCellReq{f, nil, c}
	return f
}

// String implements fmt.Stringer.
func (f *Firefly) String() string {
	return fmt.Sprintf("% 4d: % 8.2f x % 8.2f @ % 4d",
		f.id,
		f.X, f.Y, f.O,
	)
}
