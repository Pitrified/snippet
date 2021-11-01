package firefly

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestMove(t *testing.T) {
	w := NewWorld(10, 10, 100)
	cacheCosSin()

	// near the top right corner
	f := NewFirefly(99.5, 99.5, 0, 0, w)
	time.Sleep(100 * time.Millisecond)
	assert.Contains(t, w.Cells[0][0].Fireflies, f.id)
	// move to the right
	f.Move()
	time.Sleep(100 * time.Millisecond)
	assert.Contains(t, w.Cells[1][0].Fireflies, f.id)
	// move to the top
	f.O = 90 / 2
	f.Move()
	time.Sleep(100 * time.Millisecond)
	assert.Contains(t, w.Cells[1][1].Fireflies, f.id)
	// move to the left
	f.O = 180 / 2
	f.Move()
	time.Sleep(100 * time.Millisecond)
	assert.Contains(t, w.Cells[0][1].Fireflies, f.id)
	// move to the bottom
	f.O = 270 / 2
	f.Move()
	time.Sleep(100 * time.Millisecond)
	assert.Contains(t, w.Cells[0][0].Fireflies, f.id)
}
