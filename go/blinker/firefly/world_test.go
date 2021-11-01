package firefly

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMoveWrap(t *testing.T) {
	w := NewWorld(10, 10, 100)

	casesCos := []struct {
		inx, iny     int
		indx, indy   int
		wantx, wanty int
	}{
		{0, 0, 0, 0, 0, 0},
		{0, 0, 10, 10, 0, 0},
		{0, 0, -10, -10, 0, 0},
		{3, 3, -4, -4, 9, 9},
		{9, 9, 4, 4, 3, 3},
	}
	for _, c := range casesCos {
		cx, cy := w.MoveWrap(c.inx, c.iny, c.indx, c.indy)
		assert.Equal(t, cx, c.wantx, fmt.Sprintf("Failed %+v", c))
		assert.Equal(t, cy, c.wanty, fmt.Sprintf("Failed %+v", c))
	}
}
