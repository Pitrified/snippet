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

// Returns an int16 in the requested range, including extremes.
func RandRangeUint16(min, max int) int16 {
	return int16(rand.Intn(max+1-min) + min)
}

// Returns an int in the requested range, including extremes.
func RandRangeInt(min, max int) int {
	return rand.Intn(max+1-min) + min
}

// A message to be sent to the world when a firefly wants to change cell.
type ChangeCellReq struct {
	f        *Firefly
	from, to *Cell
}

// Compute the Manhattan distance on a torus between two fireflies.
func ManhattanDist(f, g *Firefly) float32 {

	// if the two are further apart than the SizeHalf
	// the shorter distance is by going around the toro
	ax := AbsFloat32(f.X - g.X)
	if ax > f.w.sizeHalfW {
		ax = f.w.SizeW - ax
	}
	ay := AbsFloat32(f.Y - g.Y)
	if ay > f.w.sizeHalfH {
		ay = f.w.SizeH - ay
	}

	return ax + ay
}

// Absolute value for float32
func AbsFloat32(a float32) float32 {
	if a < 0 {
		return -a
	}
	return a
}
