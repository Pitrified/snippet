package firefly

type Firefly struct {
	X, Y float32 // Position on the map.
	O    uint8   // Orientation in half degrees: O=3 means Deg=6.

	id int // Unique id of the firefly.
}

func NewFirefly(x, y float32, o uint8, id int) *Firefly {
	return &Firefly{x, y, o, id}
}
