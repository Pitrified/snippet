package turtle

import "math"

func intAbs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

func deg2rad(deg float64) float64 {
	return deg * math.Pi / 180
}

func rad2deg(rad float64) float64 {
	return rad / math.Pi * 180
}
