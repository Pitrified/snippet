package cellfire

import (
	"math"
	"math/rand"
)

// Precomputed values of cos/sin.
var cos, sin map[int16]float32

// Populate the double-degree cos/sin cache.
func cacheCosSin() {
	cos = make(map[int16]float32)
	sin = make(map[int16]float32)
	for o := int16(0); o < 360; o++ {
		cos[o] = float32(math.Cos(float64(o) * math.Pi / 180))
		sin[o] = float32(math.Sin(float64(o) * math.Pi / 180))
	}
}

// Returns a valid orientation in [0, 360)
func ValidateOri(o int16) int16 {
	for o < 0 {
		o += 360
	}
	for o >= 360 {
		o -= 360
	}
	return o
}

// Returns a int16 in the requested range, including extremes.
func RandRangeUint16(min, max int) int16 {
	return int16(rand.Intn(max+1-min) + min)
}

// A message to be sent to the world when a firefly wants to change cell.
type ChangeCellReq struct {
	f        *Firefly
	from, to *Cell
}
