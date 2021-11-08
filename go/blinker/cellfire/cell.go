package cellfire

import (
	"fmt"
	"sync"
)

// Cell represents a portion of the environment.
type Cell struct {
	Fireflies map[int]*Firefly // Fireflies in this cell.

	// chEnter, chLeave chan *Firefly // Channels for fireflies to enter/leave the cell.

	w                        *World  // World this cell is in.
	cx, cy                   int     // Coordinates of the cell in the world.
	top, bottom, left, right float32 // Borders of the cell.

	chRender chan byte // Channel to request a render of the cell.
	chMove   chan byte // Channel to request a move of all the fireflies in the cell.
	chBlink  chan byte // Channel to request a blink  of all the fireflies in the cell.

	blinkQueue chan *Firefly // Blinks to process.
	blinkDone  chan bool     // All the cells are done blinking and can return.

	idle     bool       // True when the blinking might be done for the cell.
	idleLock sync.Mutex // Lock to acquire before accessing idle.
}

// Create a new cell and start listening on the channels.
func NewCell(w *World, cx, cy int) *Cell {
	c := &Cell{}

	// fireflies in this cell
	c.Fireflies = make(map[int]*Firefly)

	// general info
	c.w = w
	c.cx, c.cy = cx, cy

	// channels
	c.chRender = make(chan byte)
	c.chMove = make(chan byte)
	c.chBlink = make(chan byte)
	c.blinkDone = make(chan bool)
	c.blinkQueue = make(chan *Firefly, 100)

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
	for {
		select {

		case <-c.chRender:

		case <-c.chMove:
			c.Move()

		case <-c.chBlink:
			c.Blink()

		}
	}
}

// Move performs a movement for all the fireflies in the cell.
func (c *Cell) Move() {

	// accumulate all the ChangeCellReqs
	// TODO check size of this 10
	// slower if we reduce it and we have a lot of reqs,
	// faster but we waste memory it it is large.
	reqs := make([]*ChangeCellReq, 0, 10)

	// move all the fireflies
	for _, f := range c.Fireflies {
		// get the ChangeCellReq
		r := f.Move()
		if r != nil {
			reqs = append(reqs, r)
		}
	}

	// tick the wg by one
	c.w.wgMove.Done()

	// send all the ChangeCellReq to the world
	c.w.chChangeCells <- reqs
}

// Blink performs a clock update for all the fireflies in the cell.
func (c *Cell) Blink() {

	// use a for select
	// quit
	// received a blink?

	// len(channel) to see if there are more to do
	// at the end of blinkDone check the len:
	// if 0, mark wg.Done,
	// else you dont, and for sure the World will not fire blinkDone
	// if you were waiting for a new blink or done,
	// and receive a blink: increment wg.Add again
	// if you were just looping on the blinkQueue do nothing

	// MAYBE copy the Fireflies map to Nudgeable map
	// then a firefly blinks, delete her from Nudgeable
	// and when computing the distances, use only Nudgeable
	// so the loops get shorter and there is no need to access f.nudgeable

	c.idleLock.Lock()
	c.idle = false
	c.idleLock.Unlock()

	// reset all fireflies as nudgeable
	// check if some fireflies are blinking with the current w.Clock
	// and put them on the correct queues
	for _, f := range c.Fireflies {
		f.nudgeable = true
		if f.CheckBlink() {
			c.blinkQueue <- f
			c.blinkNeighbors(f)
		}
	}
	// NOTE: all this might fire simultaneously, not just in this step
	// the first blink could nudge some of them and make them blink in step
	// eg deadlines f1 1010 f2 1020, clock 1050
	// both blink, but if f2 is in range with f1, f2 should blink at 1010
	// MAYBE do a minimal distance check only between these?
	// but also the neighboring ones...
	// The point is that if they nudge each other in this simulation step,
	// there is actually a NudgeAmount of time elapsed
	// eg deadlines f1 1010 f2 1020 f3 1015, clock 1050, all in range
	// if f3 is the first parsed in the map, f2 is nudged by her (f1 is not)
	// and we have to wait f1-f2 for the correct firing of f2 at 1010
	// so maybe we could keep computing all pairs?
	// at this point a cache of distances might be useful

	// if no firefly blinked on her own
	// mark that this cell might be done
	// (fBlink := <-c.blinkQueue might never fire, if no neighbor act)
	c.idleLock.Lock()
	if len(c.blinkQueue) == 0 {
		c.idle = true
		c.w.wgClockTick.Done()
	}
	c.idleLock.Unlock()

	for {
		select {

		case fBlink := <-c.blinkQueue:
			// fmt.Printf("blink [% 3d,% 3d] : %+v\n", c.cx, c.cy, fBlink.id)

			// if this cell had previously emptied the queue
			// mark again that we have work to do
			// NOTE: this is marked as a data race with the Wait
			// do not do the Add here, but call it inside blinkNeighbors
			// have to check if the neighbor was idling (mutex?)
			// so that Add is called well before Done
			// we do this in w.SendBlinkTo
			// (called when the other cells' goroutines do the neighbor nudge)
			// so we are sure that the add is called in the other goroutine,
			// before that goroutine ever calls Done
			// c.idleLock.Lock()
			// if c.idle {
			// 	c.w.wgClockTick.Add(1)
			// 	c.idle = false
			// }
			// c.idleLock.Unlock()

			// iterate over all nudgeable fireflies
			// if the nudged deadline is earlier than Clock
			// blink that firefly
			// put her on the blinkQueue
			// and on the blinkQueues of the neighbors

			// nudge all the fireflies
			for _, fOther := range c.Fireflies {
				// if the other already blinked in this round, skip it
				if !fOther.nudgeable {
					continue
				}
				// do not self-nudge
				// no need for this check: fBlink has nudgeable set to false
				// if fBlink.id == fOther.id { continue }
				// nudge the other
				blinked := fOther.Nudge(fBlink)
				if blinked {
					c.blinkQueue <- fOther
					// nudge the neighboring cells if close to the border
					c.blinkNeighbors(fOther)
				}
			}

			// if there are no more blinks to procees
			// mark that this cell might be done
			c.idleLock.Lock()
			if len(c.blinkQueue) == 0 {
				c.idle = true
				// NOTE: here is super shaky:
				// if the neighbors do not react quickly with blinkQueue and restart
				// the Done is called before they call Add(1)
				// and the thing starts to unravel
				c.w.wgClockTick.Done()
			}
			c.idleLock.Unlock()

		case <-c.blinkDone:
			// all the cells had empty queues
			// the World went ahead and is sending the done signals
			return

		}
	}
}

// Send the Firefly to the neighboring cells' blink queue.
func (c *Cell) blinkNeighbors(f *Firefly) {
	// MAYBE also on the corner cell
	// left
	if f.X-c.left < c.w.borderDist {
		c.w.SendBlinkTo(f, c, 'L')
	} else
	// right
	if c.right-f.X < c.w.borderDist {
		c.w.SendBlinkTo(f, c, 'R')
	}
	// bottom
	if f.Y-c.bottom < c.w.borderDist {
		c.w.SendBlinkTo(f, c, 'B')
	} else
	// top
	if c.top-f.Y < c.w.borderDist {
		c.w.SendBlinkTo(f, c, 'T')
	}
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
	s := fmt.Sprintf("[% 3d,% 3d]: % 4d @ (%8.2f, %8.2f)x(%8.2f, %8.2f)",
		c.cx, c.cy,
		len(c.Fireflies),
		c.left, c.bottom,
		c.right, c.top,
	)
	for _, f := range c.Fireflies {
		// Add the state of the firefly to the Cell repr.
		s += fmt.Sprintf("\n\tF: %v", f)
	}
	return s
}
