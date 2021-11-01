package firefly

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCellEnterLeave(t *testing.T) {
	w := NewWorld(10, 10, 100)
	c := w.Cells[0][0]
	f := NewFirefly(0, 0, 0, 0, w)
	// c.Enter(f)
	assert.Contains(t, c.Fireflies, f.id)
	c.Leave(f)
	assert.NotContains(t, c.Fireflies, f.id)
}
