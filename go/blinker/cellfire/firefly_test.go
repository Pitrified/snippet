package cellfire

import "testing"

// Check that the fields/verbs used when printing are valid.
func TestStringFirefly(t *testing.T) {
	w := NewWorld(10, 10, 100)
	c := w.Cells[0][0]
	f := NewFirefly(0, 0, 0, 0, 1000, c, w)
	f.String()
}
