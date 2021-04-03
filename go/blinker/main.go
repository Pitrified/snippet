package main

import (
	"fmt"
	"math/rand"
	"time"
)

func randSleep(sec float64, ch chan<- string) {
	time.Sleep(time.Duration(rand.Float64() * 1e9 * sec))
	ch <- "Done."
}

func randDuration(begin float64, length float64) time.Duration {
	return time.Duration((begin + rand.Float64()*length) * 1e9)
}

////////////////////////////////////////////////////////////////////////////////

// sample use of a timeout
func blinkTimeoutSingle() {
	rand.Seed(time.Now().UnixNano())

	ch := make(chan string)

	go randSleep(2, ch)

	select {
	case res := <-ch:
		fmt.Println("Got res: ", res)
	case <-time.After(1 * time.Second):
		fmt.Println("Timeout.")
	}
}

////////////////////////////////////////////////////////////////////////////////

// sample use of a ticker
func blinkTicker1() {
	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()

	// to quit the loop someday
	done := make(chan bool)
	go func() {
		time.Sleep(5 * time.Second)
		done <- true
	}()

	for {
		select {
		case <-done:
			fmt.Println("Done all!")
			return
		case t := <-ticker.C:
			fmt.Println("Current time: ", t)
		}
	}
}

////////////////////////////////////////////////////////////////////////////////

// ticker and timer together
// generate blinks every 0.8-1.2 sec
// after 1 sec blink anyway
// if the blink is forced, stop the other timer
func blinkTicker2() {
	rand.Seed(time.Now().UnixNano())

	// begin := 0.8
	// length := 0.4

	// very close to 1s, to force the flush
	begin := 0.999
	length := 0.002

	ticker := time.NewTicker(time.Second)
	timer := time.NewTimer(randDuration(begin, length))

	// to quit the loop someday
	done := make(chan bool)
	go func() {
		time.Sleep(10 * time.Second)
		done <- true
	}()

	for {
		select {
		case <-done:
			fmt.Println("Done all!")
			return
		case t := <-ticker.C:
			fmt.Println("Ticker: ", t)

			// reset the timer
			if !timer.Stop() {
				fmt.Println("Flushing timer channel.")
				<-timer.C
			}
			timer.Reset(randDuration(begin, length))

		case t := <-timer.C:
			fmt.Println("Timer : ", t)
			// reset the ticker
			ticker.Reset(time.Second)
			// reset the timer as well to restart it
			timer.Reset(randDuration(begin, length))
		}
	}
}

////////////////////////////////////////////////////////////////////////////////

// test with manipulating time
func timeDiff() {
	rand.Seed(time.Now().UnixNano())

	// setup some deadline
	now := time.Now()
	fmt.Printf("now         : %v %T\n", now, now)
	period := randDuration(0.9, 0.2)
	fmt.Printf("period      : %v %T\n", period, period)
	nextBlink := time.Now().Add(period)
	fmt.Printf("nextBlink   : %v %T\n", nextBlink, nextBlink)

	// sleep for a while
	sleep := randDuration(0.1, 0.1)
	fmt.Printf("sleep       : %v %T\n", sleep, sleep)
	time.Sleep(sleep)

	// Duration until next blink
	toNext := time.Until(nextBlink)
	fmt.Printf("toNext      : %v %T\n", toNext, toNext)
	fmt.Printf("toNext.Milliseconds() : %v %T\n", toNext.Milliseconds(), toNext.Milliseconds())
	fmt.Printf("toNext.Nanoseconds()  : %v %T\n", toNext.Nanoseconds(), toNext.Nanoseconds())
	fmt.Printf("toNext.Seconds()      : %v %T\n", toNext.Seconds(), toNext.Seconds())

	// scale the interval until the next blink
	toNextFlo := toNext.Seconds() * 0.8
	// Optionally remove a fixed amount (3ms) so that if it is really close to
	// firing, it will fire now (or just check if it is smaller than 3ms).
	// Also useful to avoid super short timer
	fmt.Printf("toNextFlo   : %v %T\n", toNextFlo, toNextFlo)
	// convert it to duration, accepts nanoseconds as int
	toNextDur := time.Duration(toNextFlo * 1e9)
	fmt.Printf("toNextDur   : %v %T\n", toNextDur, toNextDur)

	// this is the time to wait until the next blink so a ticker is actually useless
}

////////////////////////////////////////////////////////////////////////////////

// SafeTimer
type SafeTimer struct {
	*time.Timer

	nextBlink time.Time
}

func NewSafeTimer(d time.Duration) *SafeTimer {
	nextBlink := time.Now().Add(d)
	return &SafeTimer{time.NewTimer(d), nextBlink}
}

func (st *SafeTimer) SafeReset(d time.Duration) {
	// fmt.Println("SafeResetting")
	if !st.Stop() {
		// fmt.Println("Draining")
		<-st.C
	}
	// fmt.Println("Reset")
	st.BlinkReset(d)
}

func (st *SafeTimer) BlinkReset(d time.Duration) {
	st.Reset(d)
	st.nextBlink = time.Now().Add(d)
}

func blinkSafeTimer() {
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

	st := NewSafeTimer(blinkPeriod)

	for {
		select {

		case <-done:
			fmt.Println("Done all!")
			return

		case t := <-st.C:
			fmt.Println("Timer : ", t)
			st.BlinkReset(blinkPeriod)

		case ni := <-nudgeCh:
			// *here* SafeReset is needed, because st.C was not used and must be drained
			fmt.Printf("    Got nudge %+v\n", ni)

			// Duration until next blink
			toNext := time.Until(st.nextBlink)
			fmt.Printf("toNext.Seconds() : %v %T\n", toNext.Seconds(), toNext.Seconds())

			// scale the interval until the next blink
			// toNextFlo := toNext.Seconds()*0.8 - 0.05
			toNextFlo := toNext.Seconds() - 0.05
			fmt.Printf("toNextFlo        : %v %T\n", toNextFlo, toNextFlo)

			if toNextFlo < 0.05 {
				// the nudge would bring it very close to zero
				// so reset it to a full timer
				fmt.Printf("Resetting blinkPeriod = %+v\n", blinkPeriod)
				st.SafeReset(blinkPeriod)
			} else {
				// convert it to duration, accepts nanoseconds as int
				toNextDur := time.Duration(toNextFlo * 1e9)
				fmt.Printf("toNextDur        : %v %T\n", toNextDur, toNextDur)
				st.SafeReset(toNextDur)
			}

		}
	}
}

////////////////////////////////////////////////////////////////////////////////

// Firefly:
// struct that holds the end
// when nudged, compute the new end
// check if newEnd.before(Now)
//    true: blink, reset ticker
//    false: nothing
// each struct is created and then golaunched
// have to setup a nudgeable flag to avoid hyperrepetition in swarm flash
//    also nifty speedup when synced

type Firefly struct {
	ticker    *time.Ticker
	nextBlink time.Time
	period    time.Duration

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
		case fIDblink := <-f.nudgeCh:
			fmt.Printf("Nudged %d by %d.\n", f.fID, fIDblink)

		// blink
		case t := <-f.ticker.C:
			fmt.Printf("Ticked %d at: %v.%v\n", f.fID, t.Second(), t.Nanosecond())
			// this call to blink is done in doBlink
			f.blinkCh <- f
		}
	}
}

func nudger(fireflies map[int]*Firefly, blinkCh <-chan *Firefly) {
	for {
		// this Firefly just blinked
		fBlink := <-blinkCh
		for fID, fOther := range fireflies {
			// skip the current firefly
			if fBlink.fID == fID {
				continue
			}
			// if the other was nudged recently, skip it
			// or when the swarm flashes they'd get nudged a zillion times
			if !fOther.nudgeable {
				continue
			}
			// nudge the other
			// fmt.Printf("Nudging %d by %d.\n", fOther.fID, fBlink.fID)
			select {
			case fOther.nudgeCh <- fBlink.fID:
				fmt.Printf("\tFree %d by %d.\n", fOther.fID, fBlink.fID)
			default:
				fmt.Printf("\t\tFull %d by %d.\n", fOther.fID, fBlink.fID)
			}
		}
	}

}

func hatch() {
	// the swarm
	fireflies := make(map[int]*Firefly)
	nF := 10
	// nF := 5000
	// the channel where each firefly sends a bool when blinking
	blinkCh := make(chan *Firefly)
	for i := 0; i < nF; i++ {
		// blinking period
		period := randDuration(0.9, 0.2)
		ticker := time.NewTicker(period)
		nextBlink := time.Now().Add(period)
		// each firefly can be nudged independently
		nudgeCh := make(chan int)
		nudgeable := true
		fireflies[i] = &Firefly{
			ticker,
			nextBlink,
			period,
			blinkCh,
			nudgeCh,
			nudgeable,
			i,
		}
		go fireflies[i].blinker()
	}

	go nudger(fireflies, blinkCh)

	// wait a while
	time.Sleep(5 * time.Second)
	fmt.Println("Quit.")
}

func main() {
	fmt.Println("vim-go")

	// which := "single"
	// which := "ticker1"
	// which := "ticker2"
	// which := "hatch"
	// which := "timediff"
	which := "safetimer"
	fmt.Printf("Which = %+v\n", which)

	switch which {
	case "single":
		blinkTimeoutSingle()
	case "ticker1":
		blinkTicker1()
	case "ticker2":
		blinkTicker2()
	case "hatch":
		hatch()
	case "timediff":
		timeDiff()
	case "safetimer":
		blinkSafeTimer()
	}
}

// https://golang.org/pkg/time/#Timer.Reset
// https://golang.org/pkg/time/#Ticker.Reset
