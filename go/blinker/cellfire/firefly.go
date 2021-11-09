package cellfire

import "fmt"

// Firefly represents a firefly in the environment.
type Firefly struct {
	X, Y float32 // Position on the map.
	O    int16   // Orientation in degrees.

	id int // Unique id of the firefly.

	c *Cell  // Cell currently occupied.
	w *World // World this firefly is in.

	period    int  // Period between blinks for this firefly (us).
	nextBlink int  // Virtual time of the next scheduled blink (us).
	nudgeable bool // True if the firefly timer can be nudged.
}

// Create a new firefly.
//
// NOTE: The World must already be listening on chChangeCell.
func NewFirefly(
	x, y float32,
	o int16,
	id int,
	period int,
	w *World,
) *Firefly {

	// create the firefly
	f := &Firefly{}
	f.X = x
	f.Y = y
	f.O = o
	f.id = id
	f.w = w

	// validate the pos/ori
	f.w.validatePos(f)
	f.O = ValidateOri(f.O)

	// find the the right cell
	cx := int(f.X / f.w.CellSize)
	cy := int(f.Y / f.w.CellSize)
	c := f.w.Cells[cx][cy]
	f.c = c

	f.period = period
	f.nextBlink = w.Clock + RandRangeInt(1000, f.period)
	f.nudgeable = true

	// enter the right cell
	w.chChangeCell <- &ChangeCellReq{f, nil, c}
	<-w.chChangeCellDone

	return f
}

// Move the firefly.
//
// Return a ChangeCellReq if needed, nil if it stays in the same cell.
func (f *Firefly) Move() *ChangeCellReq {

	// change orientation sometimes
	newO := f.O + RandRangeUint16(-1, 1)
	f.O = ValidateOri(newO)

	// move and validate the pos
	f.X += cos[f.O]
	f.Y += sin[f.O]
	f.w.validatePos(f)

	// change cell if needed
	r := (*ChangeCellReq)(nil)
	changed := false
	dx, dy := 0, 0
	if f.X < f.c.left {
		// move to the cell to the left
		changed = true
		dx = -1
	} else if f.X > f.c.right {
		// move to the cell to the right
		changed = true
		dx = 1
	}
	if f.Y < f.c.bottom {
		// move to the cell to the bottom
		changed = true
		dy = -1
	} else if f.Y > f.c.top {
		// move to the cell to the top
		changed = true
		dy = 1
	}
	if changed {
		ncx, ncy := f.w.MoveWrap(f.c.Cx, f.c.Cy, dx, dy)
		r = &ChangeCellReq{f, f.c, f.w.Cells[ncx][ncy]}
	}

	return r
}

// Nudge the internal deadline, if the other Firefly is close.
//
// Return true if this firefly blinked.
func (f *Firefly) Nudge(fOther *Firefly) bool {
	if ManhattanDist(f, fOther) < f.w.NudgeRadius {
		f.nextBlink -= f.w.NudgeAmount
	}
	return f.CheckBlink()
}

// Check if the deadline is before the clock.
//
// Return true if the firefly blinked.
func (f *Firefly) CheckBlink() bool {
	if f.nextBlink <= f.w.Clock {
		// compute the next deadline
		f.nextBlink += f.period
		// MAYBE atomic operation?
		f.nudgeable = false
		chPrint <- "."
		return true
	}
	return false
}

// String implements fmt.Stringer.
func (f *Firefly) String() string {
	return fmt.Sprintf("% 4d: % 8.2f x % 8.2f @ % 4d",
		f.id,
		f.X, f.Y, f.O,
	)
}
