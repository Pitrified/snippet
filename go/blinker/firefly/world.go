package firefly

import (
	"fmt"
	"math/rand"
)

type World struct {
	Cells    [][]*Cell // Cells in the world.
	CellWNum int       // Width of the world in cells.
	CellHNum int       // Height of the world in cells.
	CellSize float32   // Size of the cells in pixels.
	SizeW    float32   // Width of the world in pixels.
	SizeH    float32   // Height of the world in pixels.
}

// NewWorld creates a new World.
func NewWorld(cw, ch int, cellSize float32) *World {
	w := &World{}

	w.CellSize = cellSize
	w.CellWNum = cw
	w.CellHNum = ch
	w.SizeW = float32(cw) * cellSize
	w.SizeH = float32(ch) * cellSize

	c := make([][]*Cell, cw)
	for i := 0; i < cw; i++ {
		c[i] = make([]*Cell, ch)
		for ii := 0; ii < ch; ii++ {
			c[i][ii] = NewCell(w, i, ii)
			// go c[i][ii].Listen()
		}
	}
	w.Cells = c

	return w
}

// HatchFireflies creates a swarm of fireflies.
func (w *World) HatchFireflies(n int) {
	for i := 0; i < n; i++ {
		// random pos/ori
		x := rand.Float32() * w.SizeW
		y := rand.Float32() * w.SizeH
		o := uint8(rand.Float64() * 180)

		// create the firefly
		NewFirefly(x, y, o, i, w)
	}
}

// String implements fmt.Stringer.
func (w *World) String() string {
	s := fmt.Sprintf("W: %dx%d (%.2f) %.2fx%.2f",
		w.CellWNum, w.CellHNum,
		w.CellSize,
		w.SizeW, w.SizeH,
	)
	for i := 0; i < w.CellWNum; i++ {
		for ii := 0; ii < w.CellHNum; ii++ {
			// Add the state of the cell to the World repr.
			s += fmt.Sprintf("\nC: %v",
				w.Cells[i][ii],
			)
		}
	}
	return s
}

// Move by (dcx, dcy) around the cells' toro, from cell (cx, cy).
func (w *World) MoveWrap(cx, cy, dcx, dcy int) (int, int) {
	cx += dcx
	for cx < 0 {
		cx += w.CellWNum
	}
	for cx >= w.CellWNum {
		cx -= w.CellWNum
	}
	cy += dcy
	for cy < 0 {
		cy += w.CellWNum
	}
	for cy >= w.CellWNum {
		cy -= w.CellWNum
	}
	return cx, cy
}
