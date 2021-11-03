package cellfire

import (
	"fmt"
	"math"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCacheCosSin(t *testing.T) {
	cacheCosSin()

	casesCos := []struct {
		o    int16
		want float32
	}{
		{0, 1},
		{30, float32(math.Sqrt(3) / 2)},
		{60, 0.5},
		{90, 0},
		{120, -0.5},
		{150, -float32(math.Sqrt(3) / 2)},
		{180, -1},
		{210, -float32(math.Sqrt(3) / 2)},
		{240, -0.5},
		{270, 0},
		{300, 0.5},
		{330, float32(math.Sqrt(3) / 2)},
	}
	for _, c := range casesCos {
		assert.InDelta(t, cos[c.o], c.want, 1e-6,
			fmt.Sprintf("Failed case %+v, had %+v", c, cos[c.o]))
	}

	casesSin := []struct {
		o    int16
		want float32
	}{
		{0, 0},
		{30, 0.5},
		{60, float32(math.Sqrt(3) / 2)},
		{90, 1},
		{120, float32(math.Sqrt(3) / 2)},
		{150, 0.5},
		{180, 0},
		{210, -0.5},
		{240, -float32(math.Sqrt(3) / 2)},
		{270, -1},
		{300, -float32(math.Sqrt(3) / 2)},
		{330, -0.5},
	}
	for _, c := range casesSin {
		assert.InDelta(t, sin[c.o], c.want, 1e-6,
			fmt.Sprintf("Failed case %+v, had %+v", c, sin[c.o]))
	}

}

func TestValidateOri(t *testing.T) {
	casesCos := []struct {
		in   int16
		want int16
	}{
		{0, 0},
		{15, 15},
		{179, 179},
		{180, 180},
		{359, 359},
		{360, 0},
		{720, 0},
		{-360, 0},
		{-1, 359},
	}
	for _, c := range casesCos {
		got := ValidateOri(c.in)
		assert.Equal(t, got, c.want, fmt.Sprintf("Failed case %+v, got %+v", c, got))
	}
}
