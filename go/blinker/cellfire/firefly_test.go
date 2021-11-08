package cellfire

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// Check that the fields/verbs used when printing are valid.
func TestStringFirefly(t *testing.T) {
	w := NewWorld(10, 10, 100)
	f := NewFirefly(0, 0, 0, 0, 1000, w)
	f.String()
}

func TestCheckBlink(t *testing.T) {
	w := NewWorld(10, 10, 100)

	f := NewFirefly(0, 0, 0, 0, 1000, w)
	blinked := f.CheckBlink()
	assert.Equal(t, false, blinked, "The Firefly should not have blinked.")

	w.Clock += 2000

	blinked = f.CheckBlink()
	assert.Equal(t, true, blinked, "The Firefly should have blinked.")
	assert.Equal(t, false, f.nudgeable, "The Firefly should not be nudgeable.")

}

func TestNudge(t *testing.T) {
	w := NewWorld(10, 10, 100)

	f := NewFirefly(0, 0, 0, 0, 1000, w)
	g := NewFirefly(1, 1, 0, 0, 1000, w)

	oldNextBlink := f.nextBlink
	blinked := f.Nudge(g)
	// remember that nudge also calls CheckBlink
	p := 0
	if blinked {
		p = f.period
	}
	newNextBlink := f.nextBlink
	assert.Equal(t, w.NudgeAmount, oldNextBlink-newNextBlink+p,
		"The deadline should have been nudged by w.NudgeAmount")

}