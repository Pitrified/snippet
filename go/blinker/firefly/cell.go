package firefly

type Cell struct {
	Fireflies map[int]bool
}

func NewCell() *Cell {
	return &Cell{}
}
