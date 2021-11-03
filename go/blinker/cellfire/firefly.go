package cellfire

import "fmt"

// Firefly represents a firefly in the environment.
type Firefly struct {
	X, Y float32 // Position on the map.
	O    int16   // Orientation in degrees.

	id int // Unique id of the firefly.

	c *Cell  // Cell currently occupied.
	w *World // World this firefly is in.
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

	// enter the right cell
	w.chChangeCell <- &ChangeCellReq{f, nil, c}

	return f
}

// do a movement.
// return a ChangeCellReq if needed
func (f *Firefly) Move() *ChangeCellReq {

	// change orientation sometimes
	newO := f.O + RandRangeUint16(-1, 1)
	f.O = ValidateOri(newO)

	// move
	f.X += cos[f.O]
	f.Y += sin[f.O]
	f.w.validatePos(f)

	return &ChangeCellReq{}
}

// String implements fmt.Stringer.
func (f *Firefly) String() string {
	return fmt.Sprintf("% 4d: % 8.2f x % 8.2f @ % 4d",
		f.id,
		f.X, f.Y, f.O,
	)
}
