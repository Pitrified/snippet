package cellfire

import "fmt"

// Cell represents a portion of the environment.
type Cell struct {
	Fireflies map[int]*Firefly // Fireflies in this cell.

	// chEnter, chLeave chan *Firefly // Channels for fireflies to enter/leave the cell.

	w                        *World  // World this cell is in.
	cx, cy                   int     // Coordinates of the cell in the world.
	top, bottom, left, right float32 // Borders of the cell.
}

// Create a new cell and start listening on the channels.
func NewCell(w *World, cx, cy int) *Cell {
	c := &Cell{}

	// fireflies in this cell
	c.Fireflies = make(map[int]*Firefly)

	// channels
	// c.chEnter = make(chan *Firefly)
	// c.chLeave = make(chan *Firefly)

	// general info
	c.w = w
	c.cx, c.cy = cx, cy

	// compute borders
	fcx := float32(c.cx)
	fcy := float32(c.cy)
	c.left = c.w.CellSize * fcx
	c.right = c.left + c.w.CellSize
	c.bottom = c.w.CellSize * fcy
	c.top = c.bottom + c.w.CellSize

	// start listening on the channels
	go c.Listen()

	return c
}

// Listen to all the channels to react.
func (c *Cell) Listen() {
	// for {
	// 	select {
	// 	case f := <-c.chEnter:
	// 		c.Enter(f)
	// 	case f := <-c.chLeave:
	// 		c.Leave(f)
	// 	}
	// }
}

// Enter adds a firefly to the cell.
func (c *Cell) Enter(f *Firefly) {
	c.Fireflies[f.id] = f
}

// Leave removes a firefly from the cell.
func (c *Cell) Leave(f *Firefly) {
	delete(c.Fireflies, f.id)
}

// String implements fmt.Stringer.
func (c *Cell) String() string {
	s := fmt.Sprintf("[% 3d,% 3d]: (%8.2f, %8.2f)x(%8.2f, %8.2f)",
		c.cx, c.cy,
		c.left, c.bottom,
		c.right, c.top,
	)
	for _, f := range c.Fireflies {
		// Add the state of the firefly to the Cell repr.
		s += fmt.Sprintf("\n\tF: %v", f)
	}
	return s
}
