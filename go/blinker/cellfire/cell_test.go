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

// Check that the fields/verbs used when printing are valid.
func TestStringCell(t *testing.T) {
	w := NewWorld(10, 10, 100)
	f := NewFirefly(0, 0, 0, 0, 1000, w)
	f.c.String()
}
