package cellfire

import "fmt"

// Firefly represents a firefly in the environment.
type Firefly struct {
	X, Y float32 // Position on the map.
	O    int16   // Orientation in half degrees: O=3 means Deg=6.

	id int // Unique id of the firefly.

	c *Cell  // Cell currently occupied.
	w *World // World this firefly is in.

	chMoveDone chan *ChangeCellReq // Channel for fireflies to enter/leave the cell.
}

// Create a new firefly.
func NewFirefly(x, y float32, o int16, id int, c *Cell, w *World) *Firefly {
	// create the firefly
	f := &Firefly{}
	f.X = x
	f.Y = y
	f.O = o
	f.id = id
	f.c = c
	f.w = w

	f.chMoveDone = make(chan *ChangeCellReq)

	w.chChangeCell <- &ChangeCellReq{f, nil, c}

	return f
}

func (f *Firefly) Move() {
	// do the movement
	// send a (possibly nil) request on chMoveDone
}

// String implements fmt.Stringer.
func (f *Firefly) String() string {
	return fmt.Sprintf("% 4d: % 8.2f x % 8.2f @ % 4d",
		f.id,
		f.X, f.Y, f.O,
	)
}
