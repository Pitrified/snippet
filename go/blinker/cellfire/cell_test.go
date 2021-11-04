package cellfire

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestBlinkNeighbors(t *testing.T) {
	w := NewWorld(10, 10, 100)

	// near the right top corner
	f := NewFirefly(99.5, 99.5, 0, 0, 1000, w)
	f.c.blinkNeighbors(f)
	assert.Equal(t, 1, len(w.Cells[1][0].blinkQueue),
		"The cell to the right should have received the Firefly on the blinkQueue.")
	assert.Equal(t, 1, len(w.Cells[0][1].blinkQueue),
		"The cell to the top should have received the Firefly on the blinkQueue.")

	// near the left bottom corner
	g := NewFirefly(0.5, 0.5, 0, 0, 1000, w)
	g.c.blinkNeighbors(g)
	assert.Equal(t, 1, len(w.Cells[9][0].blinkQueue),
		"The cell to the left should have received the Firefly on the blinkQueue.")
	assert.Equal(t, 1, len(w.Cells[0][9].blinkQueue),
		"The cell to the bottom should have received the Firefly on the blinkQueue.")
}

// A blinking firefly will nudge a neighbor.
func TestBlinkTwo(t *testing.T) {
	w := NewWorld(3, 3, 100)

	// f will blink immediately
	f := NewFirefly(150, 150, 0, 0, 1000000, w)
	f.nextBlink = w.Clock - 1

	// we want to see g being nudged, but not blinking
	g := NewFirefly(151, 151, 0, 1, 1000000, w)
	oldNextBlink := g.nextBlink

	w.wgClockTick.Add(1)
	go f.c.Blink()
	w.wgClockTick.Wait()

	newNextBlink := g.nextBlink
	assert.Equal(t, w.NudgeAmount, oldNextBlink-newNextBlink,
		"The deadline should have been nudged by w.NudgeAmount")
}

// A blinking firefly will nudge a neighbor, which will blink.
// The blinking propagates, and a 3rd neighbor will blink after a 2nd nudge.
func TestBlinkThree(t *testing.T) {
	w := NewWorld(3, 3, 100)

	// f1 will blink immediately
	f1 := NewFirefly(150, 150, 0, 0, 1000000, w)
	f1.nextBlink = w.Clock - 1
	// f2 will blink when nudged by f1
	f2 := NewFirefly(151, 151, 0, 1, 1000000, w)
	f2.nextBlink = w.Clock + 1
	// f3 will blink when nudged by f2
	f3 := NewFirefly(152, 152, 0, 2, 1000000, w)
	f3.nextBlink = w.Clock + 1 + w.NudgeAmount

	w.wgClockTick.Add(1)
	go f1.c.Blink()
	w.wgClockTick.Wait()

	assert.Equal(t, false, f1.nudgeable,
		"Firefly 1 should have blinked.")
	assert.Equal(t, false, f2.nudgeable,
		"Firefly 2 should have blinked.")
	assert.Equal(t, false, f3.nudgeable,
		"Firefly 3 should have blinked.")
}

// A blinking firefly nudges a neighbor in a neighboring cell.
func TestBlinkNeighbor(t *testing.T) {
	w := NewWorld(3, 3, 100)

	// f1 will blink immediately
	f1 := NewFirefly(199, 150, 0, 0, 1000000, w)
	f1.nextBlink = w.Clock - 1
	// f2 will blink when nudged by f1
	f2 := NewFirefly(201, 150, 0, 1, 1000000, w)
	f2.nextBlink = w.Clock + 1

	w.wgClockTick.Add(2)
	go f2.c.Blink() // start f2 first, so that it will pause with empty blinkQueue
	go f1.c.Blink()
	w.wgClockTick.Wait()

	assert.Equal(t, false, f1.nudgeable,
		"Firefly 1 should have blinked.")
	assert.Equal(t, false, f2.nudgeable,
		"Firefly 2 should have blinked.")
}

// Check that the fields/verbs used when printing are valid.
func TestStringCell(t *testing.T) {
	w := NewWorld(10, 10, 100)
	f := NewFirefly(0, 0, 0, 0, 1000, w)
	f.c.String()
}
