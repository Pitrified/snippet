package firefly

type World struct {
	Cells    [][]*Cell // Cells in the world.
	CellW    int       // Width of the world in cells.
	CellH    int       // Height of the world in cells.
	CellSize float32   // Size of the cells.
	SizeW    float32   // Width of the world in pixels.
	SizeH    float32   // Height of the world in pixels.
}

// NewWorld creates a new World and populates it with fireflies.
func NewWorld(cw, ch int, cellSize float32) *World {
	w := &World{}

	w.CellSize = cellSize
	w.CellW = cw
	w.CellH = ch
	w.SizeW = float32(cw) * cellSize
	w.SizeH = float32(ch) * cellSize

	c := make([][]*Cell, cw)
	for i := 0; i < cw; i++ {
		c[i] = make([]*Cell, ch)
		for ii := 0; ii < ch; ii++ {
			c[i][ii] = NewCell()
		}
	}
	w.Cells = c

	return w
}
