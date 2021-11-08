package cellfire

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestChangeCell(t *testing.T) {
	w := NewWorld(10, 10, 100)
	f := NewFirefly(0, 0, 0, 0, 1000000, w)

	c := f.c
	assert.Contains(t, c.Fireflies, f.id)

	// change cell
	nc := w.Cells[1][1]
	w.chChangeCell <- &ChangeCellReq{f, f.c, nc}
	<-w.chChangeCellDone
	assert.NotContains(t, c.Fireflies, f.id)
}

func TestMove(t *testing.T) {
	cacheCosSin()

	w := NewWorld(10, 10, 100)

	// near the top right corner, pointing right
	f := NewFirefly(99.5, 99.5, 0, 0, 1000000, w)
	assert.Contains(t, w.Cells[0][0].Fireflies, f.id)
	// move to the right
	w.Move()
	assert.Contains(t, w.Cells[1][0].Fireflies, f.id)
	// move to the top
	f.O = 90
	w.Move()
	assert.Contains(t, w.Cells[1][1].Fireflies, f.id)
	// move to the left
	f.O = 180
	w.Move()
	assert.Contains(t, w.Cells[0][1].Fireflies, f.id)
	// move to the bottom
	f.O = 270
	w.Move()
	assert.Contains(t, w.Cells[0][0].Fireflies, f.id)
}

func TestHatch(t *testing.T) {
	cacheCosSin()

	w := NewWorld(10, 10, 100)
	nF := 10
	w.HatchFireflies(nF)

	// count how many were created
	tot := 0
	for i := 0; i < w.CellWNum; i++ {
		for ii := 0; ii < w.CellHNum; ii++ {
			tot += len(w.Cells[i][ii].Fireflies)
		}
	}
	assert.Equal(t, nF, tot, fmt.Sprintf("Failed %+v, created %+v", nF, tot))

}

func TestMoveWrap(t *testing.T) {
	w := NewWorld(10, 10, 100)

	cases := []struct {
		cx, cy, dcx, dcy, nx, ny int
	}{
		{0, 0, 0, 0, 0, 0},
		{0, 0, -1, -1, 9, 9},
		{0, 0, -101, -101, 9, 9},
		{0, 0, 10, 10, 0, 0},
		{0, 0, 100, 100, 0, 0},
	}
	for _, c := range cases {
		gotX, gotY := w.MoveWrap(c.cx, c.cy, c.dcx, c.dcy)
		assert.Equal(t, gotX, c.nx, fmt.Sprintf("Failed case %+v, got %+v", c, gotX))
		assert.Equal(t, gotY, c.ny, fmt.Sprintf("Failed case %+v, got %+v", c, gotY))
	}
}

func TestValidatePos(t *testing.T) {
	w := NewWorld(10, 10, 100)

	cases := []struct {
		x, y   float32
		nx, ny float32
	}{
		{0, 0, 0, 0},
		{1010, 1010, 10, 10},
		{-10, -10, 990, 990},
	}
	for _, c := range cases {
		f := NewFirefly(c.x, c.y, 0, 0, 1000000, w)
		w.validatePos(f)
		gotX, gotY := f.X, f.Y
		assert.InDelta(t, gotX, c.nx, 1e-6, fmt.Sprintf("Failed case %+v, got %+v", c, gotX))
		assert.InDelta(t, gotY, c.ny, 1e-6, fmt.Sprintf("Failed case %+v, got %+v", c, gotY))
	}
}

func TestSendBlinkTo(t *testing.T) {
	w := NewWorld(10, 10, 100)

	// near the right top corner
	f := NewFirefly(99.5, 99.5, 0, 0, 1000000, w)
	w.SendBlinkTo(f, w.Cells[0][0], 'R')
	assert.Equal(t, 1, len(w.Cells[1][0].blinkQueue),
		"The cell to the right should have received the Firefly on the blinkQueue.")
	w.SendBlinkTo(f, w.Cells[0][0], 'T')
	assert.Equal(t, 1, len(w.Cells[0][1].blinkQueue),
		"The cell to the top should have received the Firefly on the blinkQueue.")

	// near the left bottom corner
	g := NewFirefly(0.5, 0.5, 0, 0, 1000000, w)
	w.SendBlinkTo(g, w.Cells[0][0], 'L')
	assert.Equal(t, 1, len(w.Cells[9][0].blinkQueue),
		"The cell to the left should have received the Firefly on the blinkQueue.")
	w.SendBlinkTo(g, w.Cells[0][0], 'B')
	assert.Equal(t, 1, len(w.Cells[0][9].blinkQueue),
		"The cell to the bottom should have received the Firefly on the blinkQueue.")
}

func TestClockTick(t *testing.T) {
	w := NewWorld(4, 4, 50)
	w.HatchFireflies(1000)
	s := time.Now()
	w.ClockTick()
	fmt.Printf("time.Since(s) = %+v\n", time.Since(s))
}

// Check that the fields/verbs used when printing are valid.
func TestStringWorld(t *testing.T) {
	w := NewWorld(10, 10, 100)
	w.String()
}
