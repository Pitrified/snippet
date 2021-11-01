package firefly

import (
	"math"
	"math/rand"
)

var cos, sin map[uint8]float32

// Convert orientation (half degrees) to radians.
func uint8Ori2float64Rad(d uint8) float64 {
	return float64(d) * 2 * math.Pi / 180
}

// Populate the half degree cos/sin cache.
// The map keys are half degrees, so O=3 means Deg=6.
func cacheCosSin() {
	cos = make(map[uint8]float32)
	sin = make(map[uint8]float32)
	for o := uint8(0); o < 180; o++ {
		cos[o] = float32(math.Cos(uint8Ori2float64Rad(o)))
		sin[o] = float32(math.Sin(uint8Ori2float64Rad(o)))
	}
}

// Returns a valid orientation in [0, 180)
func validateOri(o uint8) uint8 {
	if o >= 180 {
		return o - 180
	}
	return o
}

// Returns a uint8 in the requested range, including extremes.
func randUint8Range(min, max int) uint8 {
	return uint8(rand.Intn(max+1-min) + min)
}
