package main

import (
	"strconv"

	"fyne.io/fyne/v2/widget"
)

func MaxFloat32(a, b float32) float32 {
	if a > b {
		return a
	} else {
		return b
	}
}

// Extract the float64 from an entry.
func entry2F64(e *widget.Entry) (float64, error) {
	return strconv.ParseFloat(e.Text, 64)
}
