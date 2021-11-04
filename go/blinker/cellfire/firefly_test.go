package cellfire

import "testing"

// Check that the fields/verbs used when printing are valid.
func TestStringFirefly(t *testing.T) {
	w := NewWorld(10, 10, 100)
	f := NewFirefly(0, 0, 0, 0, 1000, w)
	f.String()
}
