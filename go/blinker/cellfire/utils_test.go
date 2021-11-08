package cellfire

import (
	"fmt"
	"math"
	"testing"

	"github.com/stretchr/testify/assert"
)

// The cached values of cos/sin are correct.
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

// Validate the orientation in the [0,360) interval.
func TestValidateOri(t *testing.T) {
	cases := []struct {
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
	for _, c := range cases {
		got := ValidateOri(c.in)
		assert.Equal(t, got, c.want, fmt.Sprintf("Failed case %+v, got %+v", c, got))
	}
}

// Absolute value for a float32.
func TestAbsFloat32(t *testing.T) {
	cases := []struct {
		in   float32
		want float32
	}{
		{0, 0},
		{10, 10},
		{-10, 10},
	}
	for _, c := range cases {
		got := AbsFloat32(c.in)
		assert.InDelta(t, got, c.want, 1e-6, fmt.Sprintf("Failed case %+v, got %+v", c, got))
	}
}

// Test the computed Manhattan distances on a toro.
func TestManhattanDist(t *testing.T) {
	w := NewWorld(10, 10, 100)
	cases := []struct {
		f, g *Firefly
		want float32
	}{
		{
			NewFirefly(99.5, 99.5, 0, 0, 1000000, w),
			NewFirefly(99.5, 99.5, 0, 0, 1000000, w),
			0,
		},
		{
			NewFirefly(50, 50, 0, 0, 1000000, w),
			NewFirefly(50, 950, 0, 0, 1000000, w),
			100,
		},
		{
			NewFirefly(50, 850, 0, 0, 1000000, w),
			NewFirefly(50, 950, 0, 0, 1000000, w),
			100,
		},
		{
			NewFirefly(50, 50, 0, 0, 1000000, w),
			NewFirefly(950, 50, 0, 0, 1000000, w),
			100,
		},
		{
			NewFirefly(50, 50, 0, 0, 1000000, w),
			NewFirefly(950, 950, 0, 0, 1000000, w),
			200,
		},
		{
			NewFirefly(50, 50, 0, 0, 1000000, w),
			NewFirefly(150, 150, 0, 0, 1000000, w),
			200,
		},
	}
	for _, c := range cases {
		got := ManhattanDist(c.f, c.g)
		assert.InDelta(t, got, c.want, 1e-6, fmt.Sprintf("Failed case %+v, got %+v", c, got))
	}
}
