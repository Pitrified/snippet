package firefly

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMove(t *testing.T) {
	w := NewWorld(10, 10, 100)
	cacheCosSin()

	// near the top right corner
	f := NewFirefly(99.5, 99.5, 0, 0, w)
	assert.Contains(t, w.Cells[0][0].Fireflies, f.id)
	// move to the right
	f.Move()
	assert.Contains(t, w.Cells[1][0].Fireflies, f.id)
	// move to the top
	f.O = 90 / 2
	f.Move()
	assert.Contains(t, w.Cells[1][1].Fireflies, f.id)
	// move to the left
	f.O = 180 / 2
	f.Move()
	assert.Contains(t, w.Cells[0][1].Fireflies, f.id)
	// move to the bottom
	f.O = 270 / 2
	f.Move()
	assert.Contains(t, w.Cells[0][0].Fireflies, f.id)
}
