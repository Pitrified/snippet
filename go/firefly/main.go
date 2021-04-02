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
	_ = Firefly{fID, pos, w.chBlinks[0][0]}
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
	chBlinks := make([][]chan *Firefly, worldWidthCell)

	for i := 0; i < worldWidthCell; i++ {
		cells[i] = make([]*Cell, worldHeightCell)
		chBlinks[i] = make([]chan *Firefly, worldHeightCell)

		for j := 0; j < worldHeightCell; j++ {
			// create channel for this cell (and the fireflies that will be in it)
			chBlinks[i][j] = make(chan *Firefly)

			// create each cell
			lefttop := WorldPos{cellSize * float64(i), cellSize * float64(j)}
			cells[i][j] = NewCell(lefttop, cellSize, chBlinks[i][j])
		}
	}

	return &World{
		worldWidthCell,
		worldHeightCell,
		cellSize,
		cells,
		chBlinks,
	}
}

type World struct {
	worldWidthCell  int
	worldHeightCell int
	cellSize        float64

	cells    [][]*Cell
	chBlinks [][]chan *Firefly
}

type WorldPos struct {
	x float64
	y float64
}

// -----------------------------------------------------------------------------
//    CELL
// -----------------------------------------------------------------------------

func NewCell(
	lefttop WorldPos,
	cellSize float64,
	chBlink <-chan *Firefly,
) *Cell {

	// cell boundaries
	left := lefttop.x
	top := lefttop.y
	right := left + cellSize
	bottom := top + cellSize

	// fireflies in this cell
	fireflies := make(map[int]*Firefly)

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

	chBlink <-chan *Firefly
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
