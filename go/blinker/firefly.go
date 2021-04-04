package main

import (
	"fmt"
	"time"
)

// Firefly:
// struct that holds the end in a BlinkTimer
// when nudged, compute the new end
// check if newEnd.before(Now)
//    true: blink, reset timer with original period
//    false: reset the timer with the new duration of time left
// each struct is created and then golaunched
// have to setup a nudgeable flag to avoid hyperrepetition in swarm flash
//    also nifty speedup when synced

type Firefly struct {
	blinkTimer    *BlinkTimer
	period        time.Duration
	postBlinkWait time.Duration

	blinkCh   chan<- *Firefly
	nudgeCh   chan int
	nudgeable bool

	fID int
}

func (f *Firefly) blinker() {
	for {
		select {

		// move nextBlink in the past proportionally to the distance to that instant
		// IF it is now in the past
		// or MAYBE blink and reset the ticker
		// or MAYBE do not blink here, but set a ticker for 1us
		// or MAYBE call a blink func eh?
		// case fIDblink := <-f.nudgeCh:
		case <-f.nudgeCh:
			// fmt.Printf("    Nudged %d by %d.\n", f.fID, fIDblink)
			f.doNudge()

		// blink
		// case t := <-f.blinkTimer.C:
		case <-f.blinkTimer.C:
			// fmt.Printf("Timer fired %d at: %v.%v\n", f.fID, t.Second(), t.Nanosecond())
			f.doBlink("timer")
		}
	}
}

func (f *Firefly) doNudge() {
	// Duration until next blink
	toNext := time.Until(f.blinkTimer.nextBlink)
	// scale the interval until the next blink
	// toNextFlo := toNext.Seconds()*0.8 - 0.05
	toNextFlo := toNext.Seconds() - 0.05

	if toNextFlo < 0.05 {
		// the nudge would bring it very close to zero
		// so reset it to a full timer
		// fmt.Printf("Resetting blinkPeriod %d = %+v\n", f.fID, f.period)
		// f.blinkTimer.SafeReset(f.period)
		f.doBlink("nudge")
	} else {
		// convert it to duration, accepts nanoseconds as int
		toNextDur := time.Duration(toNextFlo * 1e9)
		// fmt.Printf("Time left %d: %v %T\n", f.fID, toNextDur, toNextDur)
		f.blinkTimer.SafeReset(toNextDur)
	}
}

func (f *Firefly) doBlink(which string) {
	// t := time.Now()
	// fmt.Printf("Blinking %d at %v.%v\n", f.fID, t.Second(), t.Nanosecond())
	fmt.Printf(".")

	// this Firefly is blinking now
	f.blinkCh <- f
	// restart the timer
	switch which {
	case "nudge":
		f.blinkTimer.SafeReset(f.period)
	case "timer":
		f.blinkTimer.BlinkReset(f.period)
	}
	// for a while this Firefly cannot be nudged
	f.nudgeable = false
	time.Sleep(f.postBlinkWait)
	f.nudgeable = true
}

func nudger(fireflies map[int]*Firefly, blinkCh <-chan *Firefly, nF int) {
	for {
		// this Firefly just blinked
		fBlink := <-blinkCh
		for fID, fOther := range fireflies {
			// skip the current firefly
			if fBlink.fID == fID {
				continue
			}
			// if the other blinked recently, skip it
			// or when the swarm flashes they'd get nudged a zillion times
			if !fOther.nudgeable {
				continue
			}
			// can only communicate between fireflies with similar fID
			if intAbs(fBlink.fID-fOther.fID)%nF > 5 {
				continue
			}
			// nudge the other
			// fmt.Printf("Nudging %d by %d.\n", fOther.fID, fBlink.fID)
			select {
			case fOther.nudgeCh <- fBlink.fID:
				// fmt.Printf("        Free %d by %d.\n", fOther.fID, fBlink.fID)
			default:
				// fmt.Printf("            Full %d by %d.\n", fOther.fID, fBlink.fID)
			}
		}
	}

}

func hatch() {

	// the swarm
	fireflies := make(map[int]*Firefly)
	// nF := 10
	nF := 50
	// nF := 500
	// nF := 5000

	// time to wait after blinking
	postBlinkWait := time.Millisecond * 200

	// the channel where each firefly sends a bool when blinking
	blinkCh := make(chan *Firefly)

	// create the fireflies
	for i := 0; i < nF; i++ {
		// blinking period
		period := randDuration(0.9, 0.2)
		// time left before this Firefly blinks
		blinkTimer := NewBlinkTimer(randDuration(0.1, 1))
		// each firefly can be nudged independently
		nudgeCh := make(chan int)
		// can be nudged for now
		nudgeable := true
		fireflies[i] = &Firefly{
			blinkTimer,
			period,
			postBlinkWait,
			blinkCh,
			nudgeCh,
			nudgeable,
			i,
		}
		go fireflies[i].blinker()
	}

	go nudger(fireflies, blinkCh, nF)

	// wait a while
	time.Sleep(600 * time.Second)
	fmt.Println("Quit.")
}
