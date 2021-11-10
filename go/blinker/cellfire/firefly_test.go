package cellfire

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// Check that the fields/verbs used when printing are valid.
func TestStringFirefly(t *testing.T) {
	w := NewWorld(3, 3, 100, 1_000_000, 25_000, 50_000, 50, 500_000, 900_000, 1_1000_000)
	f := NewFirefly(0, 0, 0, 0, 1000000, w)
	f.String()
}

func TestCheckBlink(t *testing.T) {
	w := NewWorld(3, 3, 100, 1_000_000, 25_000, 50_000, 50, 500_000, 900_000, 1_1000_000)

	f := NewFirefly(0, 0, 0, 0, 1000000, w)
	blinked := f.CheckBlink()
	assert.Equal(t, false, blinked, "The Firefly should not have blinked.")

	w.Clock += 2000000

	blinked = f.CheckBlink()
	assert.Equal(t, true, blinked, "The Firefly should have blinked.")
	assert.Equal(t, false, f.nudgeable, "The Firefly should not be nudgeable.")

}

func TestNudge(t *testing.T) {
	w := NewWorld(3, 3, 100, 1_000_000, 25_000, 50_000, 50, 500_000, 900_000, 1_1000_000)

	f := NewFirefly(0, 0, 0, 0, 1000000, w)
	g := NewFirefly(1, 1, 0, 0, 1000000, w)

	oldNextBlink := f.NextBlink
	blinked := f.Nudge(g)
	// remember that nudge also calls CheckBlink
	p := 0
	if blinked {
		p = f.Period
	}
	newNextBlink := f.NextBlink
	assert.Equal(t, w.NudgeAmount, oldNextBlink-newNextBlink+p,
		"The deadline should have been nudged by w.NudgeAmount")

}
