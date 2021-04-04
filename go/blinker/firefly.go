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
	fID int

	blinkTimer    *BlinkTimer
	period        time.Duration
	postBlinkWait time.Duration

	blinkCh   chan<- *Firefly
	nudgeCh   chan int
	nudgeable bool

	printCh chan<- string
	writeCh chan<- string
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

// this Firefly is blinking now
func (f *Firefly) doBlink(source string) {
	t := time.Now()

	// print to screen
	// fmt.Printf("Blinking %d at %v.%v\n", f.fID, t.Second(), t.Nanosecond())
	// fmt.Printf(".")
	f.printCh <- "."

	// write to file (homegrown csv)
	// f.writeCh <- fmt.Sprintf("%v,%v\n", t.Second(), t.Nanosecond()/1e6)
	f.writeCh <- fmt.Sprintf("%v,%v,%v\n", f.fID, t.Second(), t.Nanosecond()/1e6)

	// send blink to nudgeCentral
	f.blinkCh <- f

	// restart the timer, also drain the channel if nudging
	switch source {
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

// when a Firefly blinks, this will send the nudge signal to all neighbours
func nudgeCentral(fireflies map[int]*Firefly, blinkCh <-chan *Firefly, nF int, nComm int) {
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
			minDist := intAbs(fBlink.fID - fOther.fID)
			if minDist > nF/2 {
				minDist = nF - minDist
			}
			if minDist > nComm {
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

func hatch(nF, nComm int) {

	// the swarm
	fireflies := make(map[int]*Firefly)

	// channel to print dots on
	printCh := make(chan string)
	printDoneCh := make(chan bool)
	go centralPrinter(printCh, printDoneCh)

	// channel to save blinks to file
	writeCh := make(chan string)
	writeDoneCh := make(chan bool)
	fileName := fmt.Sprintf("histBlinkID_%v_%v.txt", nF, nComm)
	go centralWriter(writeCh, writeDoneCh, fileName)

	// time to wait after blinking
	postBlinkWait := time.Millisecond * 200

	// the channel where each firefly sends a bool when blinking
	blinkCh := make(chan *Firefly)

	// create the fireflies
	for i := 0; i < nF; i++ {
		// time left before this Firefly blinks
		blinkTimer := NewBlinkTimer(randDuration(0.1, 1))
		// blinking period
		period := randDuration(0.9, 0.2)
		// each firefly can be nudged independently
		nudgeCh := make(chan int)
		// can be nudged right now
		nudgeable := true
		fireflies[i] = &Firefly{
			i,

			blinkTimer,
			period,
			postBlinkWait,

			blinkCh,
			nudgeCh,
			nudgeable,

			printCh,
			writeCh,
		}
		go fireflies[i].blinker()
	}

	go nudgeCentral(fireflies, blinkCh, nF, nComm)

	// wait a while
	time.Sleep(600 * time.Second)
	fmt.Println("Quit.")

	// close writer and wait for it to flush
	writeDoneCh <- true
	<-writeDoneCh
}
