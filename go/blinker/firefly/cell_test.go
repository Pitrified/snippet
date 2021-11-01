package firefly

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestCellEnterLeave(t *testing.T) {
	w := NewWorld(10, 10, 100)
	c := w.Cells[0][0]
	f := NewFirefly(0, 0, 0, 0, w)

	time.Sleep(100 * time.Millisecond)
	assert.Contains(t, c.Fireflies, f.id)

	c.chLeave <- f
	time.Sleep(100 * time.Millisecond)
	assert.NotContains(t, c.Fireflies, f.id)
}
