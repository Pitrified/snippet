package firefly

import "math"

var cos, sin map[uint8]float32

// Convert degrees to radians.
func uint8Deg2float64Rad(d uint8) float64 {
	return float64(d) * math.Pi / 180
}

// Populate the half degree cos/sin cache.
// The map keys are half degrees, so O=3 means Deg=6.
func cacheCosSin() {
	cos = make(map[uint8]float32)
	sin = make(map[uint8]float32)
	for o := uint8(0); o < 180; o++ {
		cos[o] = float32(math.Cos(uint8Deg2float64Rad(o * 2)))
		sin[o] = float32(math.Sin(uint8Deg2float64Rad(o * 2)))
	}
}
