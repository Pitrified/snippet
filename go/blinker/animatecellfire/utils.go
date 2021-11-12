package main

import (
	"blinker/cellfire"
)

func MaxFloat32(a, b float32) float32 {
	if a > b {
		return a
	} else {
		return b
	}
}

// // Extract the float64 from an entry.
// func entry2F64(e *widget.Entry) (float64, error) {
// 	return strconv.ParseFloat(e.Text, 64)
// }

// https://stackoverflow.com/q/23482786/2237151
func getMapKey(m map[int]*cellfire.Firefly) int {
	for k := range m {
		return k
	}
	return -1
}
