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

	PrinterInit(50)

	clockStart, clockTickLen := 1_000_000, 25_000
	// nudgeAmount := 50_000
	nudgeAmount := 100_000
	nudgeRadius := float32(50)
	// nudgeRadius := float32(100)
	blinkCooldown := 200_000
	periodMin, periodMax := 900_000, 1_1000_000

	w := NewWorld(
		cw, ch, cellSize,
		clockStart, clockTickLen,
		nudgeAmount, nudgeRadius,
		blinkCooldown,
		periodMin, periodMax,
	)

	w.HatchFireflies(nF)

	if cw*ch < 15 && nF < 100 {
		fmt.Printf("%+v\n", w)
	}

	N := 10 * 40 // n seconds * tick per second
	s := time.Now()
	for i := 0; i < N; i++ {
		w.Step()
		// if i%40 == 0 {
		// if i%4 == 0 {
		chPrint <- fmt.Sprintf("%d: %dus\n", i, w.Clock)
		// }
	}
	fmt.Printf("Simulated %+v s in %+v\n", N*w.ClockTickLen/1_000_000, time.Since(s))
}
