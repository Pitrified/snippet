package main

import (
	"fmt"
	"math/rand"
	"time"
)

func blinkBlinkTimer() {
	rand.Seed(time.Now().UnixNano())

	nudgePeriod := time.Duration(0.9 * 1e9)
	blinkPeriodSec := 1.0
	blinkPeriod := time.Duration(blinkPeriodSec * 1e9)

	// nudge every shorter period
	nudgeCh := make(chan int)
	go func() {
		for i := 0; ; i++ {
			time.Sleep(nudgePeriod)
			// fmt.Printf("Sending nudge %+v\n", i)
			nudgeCh <- i
			// add more nudgers (more neighbours)
			// this is the expected behaviour
			// but the post-blink inhibitor is needed
			nudgeCh <- i
			nudgeCh <- i
			// fmt.Printf("   Sent nudge %+v\n", i)
		}
	}()

	// to quit the loop someday
	done := make(chan bool)
	go func() {
		time.Sleep(50 * time.Second)
		done <- true
	}()

	// sleep a random amount to desync the two
	time.Sleep(time.Duration(rand.Float64() * 1e9))

	// create the BlinkTimer
	bt := NewBlinkTimer(blinkPeriod)

	for {
		select {

		case <-done:
			fmt.Println("Done all!")
			return

		case t := <-bt.C:
			fmt.Println("Timer : ", t)
			bt.BlinkReset(blinkPeriod)

		case ni := <-nudgeCh:
			// *here* SafeReset is needed, because bt.C was not used and must be drained
			fmt.Printf("    Got nudge %+v\n", ni)

			// Duration until next blink
			toNext := time.Until(bt.nextBlink)
			fmt.Printf("toNext.Seconds() : %v %T\n", toNext.Seconds(), toNext.Seconds())

			// scale the interval until the next blink
			// toNextFlo := toNext.Seconds()*0.8 - 0.05
			toNextFlo := toNext.Seconds() - 0.05
			fmt.Printf("toNextFlo        : %v %T\n", toNextFlo, toNextFlo)

			if toNextFlo < 0.05 {
				// the nudge would bring it very close to zero
				// so reset it to a full timer
				fmt.Printf("Resetting blinkPeriod = %+v\n", blinkPeriod)
				bt.SafeReset(blinkPeriod)
			} else {
				// convert it to duration, accepts nanoseconds as int
				toNextDur := time.Duration(toNextFlo * 1e9)
				fmt.Printf("toNextDur        : %v %T\n", toNextDur, toNextDur)
				bt.SafeReset(toNextDur)
			}

		}
	}
}
