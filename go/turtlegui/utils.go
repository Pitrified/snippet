package main

import (
	"fmt"
	"strconv"
	"strings"

	"fyne.io/fyne/v2/widget"
)

// Extract the float64 from an entry.
func entry2F64(e *widget.Entry) (float64, error) {
	return strconv.ParseFloat(e.Text, 64)
}

// Prettier format for floats, remove trailing zeros.
// https://stackoverflow.com/q/31289409/2237151
func FormatFloat(num float64, prc int) string {
	str := fmt.Sprintf("%."+strconv.Itoa(prc)+"f", num)
	return strings.TrimRight(strings.TrimRight(str, "0"), ".")
}
