package firefly

import "fmt"

type Firefly struct {
	X, Y float32 // Position on the map.
	O    uint8   // Orientation in half degrees: O=3 means Deg=6.

	id int // Unique id of the firefly.

	c *Cell  // Cell currently occupied.
	w *World // World this firefly is in.
}

// Create a new firefly.
//
// NOTE: The cells must already be listening for the firefly to enter.
func NewFirefly(x, y float32, o uint8, id int, w *World) *Firefly {
	// find the the right cell
	cx := int(x / w.CellSize)
	cy := int(y / w.CellSize)
	c := w.Cells[cx][cy]

	// create the firefly
	f := &Firefly{x, y, validateOri(o), id, c, w}

	// enter the right cell
	c.chEnter <- f

	return f
}

// Change orientation and move the firefly.
func (f *Firefly) Move() {
	// change orientation sometimes
	newO := f.O + randUint8Range(-1, 1)
	f.O = validateOri(newO)

	// move
	f.X += cos[f.O]
	f.Y += sin[f.O]

	// change cell if needed
	if f.X < f.c.left {
		// move to cell to the left
		f.c.chLeave <- f
		ncx, ncy := f.w.MoveWrap(f.c.cx, f.c.cy, -1, 0)
		f.c = f.w.Cells[ncx][ncy]
		f.c.chEnter <- f
	}
	if f.X > f.c.right {
		// move to cell to the right
		f.c.chLeave <- f
		ncx, ncy := f.w.MoveWrap(f.c.cx, f.c.cy, 1, 0)
		f.c = f.w.Cells[ncx][ncy]
		f.c.chEnter <- f
	}
	if f.Y < f.c.bottom {
		// move to cell to the bottom
		f.c.chLeave <- f
		ncx, ncy := f.w.MoveWrap(f.c.cx, f.c.cy, 0, -1)
		f.c = f.w.Cells[ncx][ncy]
		f.c.chEnter <- f
	}
	if f.Y > f.c.top {
		// move to cell to the top
		f.c.chLeave <- f
		ncx, ncy := f.w.MoveWrap(f.c.cx, f.c.cy, 0, 1)
		f.c = f.w.Cells[ncx][ncy]
		f.c.chEnter <- f
	}
}

// String implements fmt.Stringer.
func (f *Firefly) String() string {
	return fmt.Sprintf("% 4d: % 8.2f x % 8.2f @ % 4d",
		f.id,
		f.X, f.Y, f.O,
	)
}
