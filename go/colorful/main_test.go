package main

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCheckBlink(t *testing.T) {
	casesCos := []struct {
		o    int16
		want int
	}{
		{0, 0},
		{5, 0},
		{350, 0},
		{25, 1},
		{45, 1},
		{45 - 22, 1},
		{45 + 22, 1},
		{45 + 23, 2},
		{45*2 - 22, 2},
		{45*2 + 22, 2},
		{45*3 - 22, 3},
		{45*3 + 22, 3},
		{45*4 - 22, 4},
		{45*4 + 22, 4},
		{45*5 - 22, 5},
		{45*5 + 22, 5},
		{45*6 - 22, 6},
		{45*6 + 22, 6},
		{45*7 - 22, 7},
		{45*7 + 22, 7},
	}
	for _, c := range casesCos {
		_, r := findBlitPos(c.o, 1, 1, 2)
		assert.Equal(t, r, c.want,
			fmt.Sprintf("Failed case %+v, had %+v", c, r))
	}
}
