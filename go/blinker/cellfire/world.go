package cellfire

import (
	"fmt"
	"math/rand"
	"sync"
)

// World represents the whole environment.
type World struct {
	Cells    [][]*Cell // Cells in the world.
	CellWNum int       // Width of the world in cells.
	CellHNum int       // Height of the world in cells.
	CellSize float32   // Size of the cells in pixels.
	SizeW    float32   // Width of the world in pixels.
	SizeH    float32   // Height of the world in pixels.

	Clock        int            // Internal time of the simulation, in us.
	ClockTickLen int            // Update per tick.
	wgClockTick  sync.WaitGroup // WG to sync the blinking
	NudgeAmount  int            // How much to nudge the firefly deadlines.

	chChangeCell     chan *ChangeCellReq   // A firefly needs to enter/leave the cell.
	chChangeCellDone chan bool             // The cell change is done.
	chChangeCells    chan []*ChangeCellReq // Channel for many fireflies to enter/leave the cell.

	chRender chan byte // Channel to request a render of the env.

	chStep chan byte // Channel to request a step of the env.

	wgMove sync.WaitGroup // WG to sync the steps
}

// NewWorld creates a new World.
func NewWorld(cw, ch int, cellSize float32) *World {
	w := &World{}

	// general params
	w.CellSize = cellSize
	w.CellWNum = cw
	w.CellHNum = ch
	w.SizeW = float32(cw) * cellSize
	w.SizeH = float32(ch) * cellSize

	w.ClockTickLen = 1000  // 1 ms
	w.Clock = 1_000_000    // start at 1 second
	w.NudgeAmount = 50_000 // 50 ms

	// channels
	w.chChangeCell = make(chan *ChangeCellReq)
	w.chChangeCellDone = make(chan bool)
	w.chChangeCells = make(chan []*ChangeCellReq)
	w.chRender = make(chan byte)
	w.chStep = make(chan byte)

	// create the cells
	c := make([][]*Cell, cw)
	for i := 0; i < cw; i++ {
		c[i] = make([]*Cell, ch)
		for ii := 0; ii < ch; ii++ {
			c[i][ii] = NewCell(w, i, ii)
		}
	}
	w.Cells = c

	// start listening
	go w.Listen()

	return w
}

// HatchFireflies creates a swarm of fireflies.
func (w *World) HatchFireflies(n int) {
	for i := 0; i < n; i++ {
		// random pos/ori
		x := rand.Float32() * w.SizeW
		y := rand.Float32() * w.SizeH
		o := int16(rand.Float64() * 360)

		// find the the right cell
		cx := int(x / w.CellSize)
		cy := int(y / w.CellSize)
		c := w.Cells[cx][cy]

		// 0.9-1.1 s
		p := RandRangeInt(900_000, 1_100_000)

		// create the firefly
		NewFirefly(x, y, o, i, p, c, w)
	}
}

// Listen to all the channels to react.
func (w *World) Listen() {
	for {
		select {

		case r := <-w.chChangeCell:
			w.ChangeCell(r)
			w.chChangeCellDone <- true

		// render the env
		case <-w.chRender:

		// tick forward the env
		case <-w.chStep:
			w.Step()
		}
	}
}

// Perform a step of the simulation.
func (w *World) Step() {

	// ##### MOVE #####
	w.Move()

	// ##### BLINK #####
	w.ClockTick()

}

// Perform a movement of the fireflies.
func (w *World) Move() {

	// move all the fireflies
	for i := 0; i < w.CellWNum; i++ {
		for ii := 0; ii < w.CellHNum; ii++ {
			w.Cells[i][ii].chMove <- 'M'
			w.wgMove.Add(1)
		}
	}

	// wait for the wg to be done
	// so that all the fireflies are done moving
	// and no cell is still iterating on c.Fireflies
	w.wgMove.Wait()

	// perform all the cell change
	for i := 0; i < w.CellWNum; i++ {
		for ii := 0; ii < w.CellHNum; ii++ {
			reqs := <-w.chChangeCells
			for _, r := range reqs {
				w.ChangeCell(r)
			}
		}
	}

}

// Perform a clock tick and blink the fireflies.
func (w *World) ClockTick() {
	w.Clock += w.ClockTickLen

	// blink all the fireflies
	for i := 0; i < w.CellWNum; i++ {
		for ii := 0; ii < w.CellHNum; ii++ {
			w.Cells[i][ii].chBlink <- 'B'
			w.wgClockTick.Add(1)
		}
	}
	w.wgClockTick.Wait()

	// TODO here send a signal on all cell channels
	// to quit blinking

}

// ChangeCell carries out the received ChangeCellReq.
// Moving a firefly from a cell to another.
func (w *World) ChangeCell(r *ChangeCellReq) {
	// update the cells
	if r.from != nil {
		r.from.Leave(r.f)
	}
	r.to.Enter(r.f)
	// update the info inside the firefly
	r.f.c = r.to
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

// Ensure that this firefly is in a valid world position.
func (w *World) validatePos(f *Firefly) {
	for f.X < 0 {
		f.X += w.SizeW
	}
	for f.X >= w.SizeW {
		f.X -= w.SizeW
	}
	for f.Y < 0 {
		f.Y += w.SizeH
	}
	for f.Y >= w.SizeH {
		f.Y -= w.SizeH
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
