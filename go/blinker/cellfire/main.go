package cellfire

import (
	"fmt"
	"time"
)

func StartFire(
	cw, ch int,
	cellSize float32,
	nF int,
) {
	cacheCosSin()

	go Printer()

	w := NewWorld(cw, ch, cellSize)

	w.HatchFireflies(nF)

	if cw*ch < 15 && nF < 100 {
		fmt.Printf("%+v\n", w)
	}

	N := 10 * 40
	s := time.Now()
	for i := 0; i < N; i++ {
		w.Step()
		// if i%40 == 0 {
		if i%4 == 0 {
			chPrint <- fmt.Sprintf("%d: %dus\n", i, w.Clock)
		}
	}
	fmt.Printf("Simulated %+v s in %+v\n", N*w.ClockTickLen/1_000_000, time.Since(s))
}
