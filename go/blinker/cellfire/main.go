package cellfire

import "fmt"

func StartFire(
	cw, ch int,
	cellSize float32,
	nF int,
) {
	cacheCosSin()

	w := NewWorld(cw, ch, cellSize)

	w.HatchFireflies(nF)

	fmt.Printf("%+v\n", w)
}
