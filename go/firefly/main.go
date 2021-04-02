package main

import "fmt"

func main() {
	fmt.Println("vim-go")

	worldWidthCell := 5
	worldHeightCell := 5
	cellSize := 10.0

	w := NewWorld(worldWidthCell, worldHeightCell, cellSize)

	createFireflies(w)
}

func createFireflies(
	w *World,
) {
	fID := 1
	pos := WorldPos{1, 1}
	_ = Firefly{fID, pos, w.cells[0][0].chBlink}
}

// -----------------------------------------------------------------------------
//    WORLD
// -----------------------------------------------------------------------------

func NewWorld(
	worldWidthCell int,
	worldHeightCell int,
	cellSize float64,
) *World {

	cells := make([][]*Cell, worldWidthCell)
	for i := 0; i < worldWidthCell; i++ {
		cells[i] = make([]*Cell, worldHeightCell)
		for j := 0; j < worldHeightCell; j++ {
			lefttop := WorldPos{cellSize * float64(i), cellSize * float64(j)}
			// create each cell
			cells[i][j] = NewCell(lefttop, cellSize)
		}
	}

	return &World{
		worldWidthCell,
		worldHeightCell,
		cellSize,
		cells,
	}
}

type World struct {
	worldWidthCell  int
	worldHeightCell int
	cellSize        float64

	cells [][]*Cell
}

type WorldPos struct {
	x float64
	y float64
}

// -----------------------------------------------------------------------------
//    CELL
// -----------------------------------------------------------------------------

// https://golang.org/doc/effective_go#composite_literals
func NewCell(lefttop WorldPos, cellSize float64) *Cell {

	// cell boundaries
	left := lefttop.x
	top := lefttop.y
	right := left + cellSize
	bottom := top + cellSize

	// fireflies in this cell
	fireflies := make(map[int]*Firefly)

	// all fireflies in this cell will send here
	chBlink := make(chan *Firefly)

	return &Cell{
		lefttop,
		cellSize,
		left,
		right,
		top,
		bottom,
		fireflies,
		chBlink,
	}
}

type Cell struct {
	lefttop  WorldPos
	cellSize float64

	left   float64
	right  float64
	top    float64
	bottom float64

	fireflies map[int]*Firefly

	// chBlink <-chan *Firefly
	chBlink chan *Firefly
}

// -----------------------------------------------------------------------------
//    FIREFLY
// -----------------------------------------------------------------------------

type Firefly struct {
	fID int

	pos WorldPos

	chBlink chan<- *Firefly
}

// type Vertex struct {
// 	X float64
// 	Y float64
// }
// // with a pointer receiver, Scale operates on the instance, not on a copy
// func (v *Vertex) Scale(f float64) {
// 	if v == nil {
// 		fmt.Println("Cannot scale a nil *Vertex")
// 		return
// 	}
// 	v.X = v.X * f
// 	v.Y = v.Y * f
// }

// type IPAddr [4]byte
// func (p IPAddr) String() string {
// 	return fmt.Sprintf("%v.%v.%v.%v", p[0], p[1], p[2], p[3])
// }
// create the error struct
// type IPError struct {
// 	Which IPAddr
// 	What  string
// }
// format the error
// // https://tour.golang.org/methods/19
// func (p *IPError) Error() string {
// 	return fmt.Sprintf("IPError at %v, %v", p.Which, p.What)
// }
// return the error as err
// func (p IPAddr) FakeSetFirst(v int) (IPAddr, error) {
// 	if v > 255 {
// 		fmt.Println("Too big, erroring")
// 		return p, &IPError{p, "Too big"}
// 	}
// 	return p, nil
// }
