package firefly

import "fmt"

type Firefly struct {
	X, Y float32 // Position on the map.
	O    uint8   // Orientation in half degrees: O=3 means Deg=6.

	id int // Unique id of the firefly.

	c *Cell  // Cell currently occupied.
	w *World // World this firefly is in.
}

func NewFirefly(x, y float32, o uint8, id int, c *Cell) *Firefly {
	return &Firefly{x, y, validateOri(o), id, c, c.w}
}

func (f *Firefly) Move() {
	// change orientation sometimes

	// move
	f.X += cos[f.O]
	f.Y += sin[f.O]

	// change cell if needed
	if f.X < f.c.left {
		// move to cell to the left
		f.c.Leave(f)
		newCell := f.w.Cells[0][0]
		f.c = newCell
		f.c.Enter(f)
	}
}

// String implements fmt.Stringer.
func (f *Firefly) String() string {
	return fmt.Sprintf("% 4d: % 8.2f x % 8.2f @ % 4d",
		f.id,
		f.X, f.Y, f.O,
	)
}
