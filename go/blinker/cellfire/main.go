package cellfire

import "fmt"

func StartFire() {
	fmt.Println("vim-go")

	cacheCosSin()

	cw, ch := 3, 3
	cellSize := float32(100)
	w := NewWorld(cw, ch, cellSize)

	nF := 10
	w.HatchFireflies(nF)

	fmt.Printf("%+v\n", w)
}
