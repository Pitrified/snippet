package cellfire

import "testing"

// Check that the fields/verbs used when printing are valid.
func TestStringCell(t *testing.T) {
	w := NewWorld(10, 10, 100)
	c := w.Cells[0][0]
	NewFirefly(0, 0, 0, 0, 1000, c, w)
	c.String()
}
