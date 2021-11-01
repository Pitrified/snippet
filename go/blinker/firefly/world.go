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
		}
	}
	w.Cells = c

	return w
}

// HatchFireflies creates a swarm of fireflies.
func (w *World) HatchFireflies(n int) {
	for i := 0; i < n; i++ {
		// create the firefly
		x := rand.Float32() * w.SizeW
		y := rand.Float32() * w.SizeH
		o := uint8(rand.Int())
		f := NewFirefly(x, y, o, i)

		// place the firefly in the right cell
		cx := int(x / w.CellSize)
		cy := int(y / w.CellSize)
		w.Cells[cx][cy].Enter(f)
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
			s += fmt.Sprintf("\nC[% 3d,% 3d]: %v",
				i, ii,
				w.Cells[i][ii],
			)
		}
	}
	return s
}
