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

func Abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
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

// BlinkTimer
type BlinkTimer struct {
	*time.Timer

	nextBlink time.Time
}

func NewBlinkTimer(d time.Duration) *BlinkTimer {
	nextBlink := time.Now().Add(d)
	return &BlinkTimer{time.NewTimer(d), nextBlink}
}

// bt.Stop is false if the timer has has already expired or been stopped
// in that case you need to drain the channel
// (when it expired the timer put a value there)
// but remember that if another goroutine extracted that value
// this will lock on <-bt.C
// MAYBE using a select with a default could be safer
func (bt *BlinkTimer) SafeReset(d time.Duration) {
	// fmt.Println("SafeResetting")
	if !bt.Stop() {
		// fmt.Println("Draining")
		<-bt.C
	}
	// fmt.Println("Reset")
	bt.BlinkReset(d)
}

func (bt *BlinkTimer) BlinkReset(d time.Duration) {
	bt.Reset(d)
	bt.nextBlink = time.Now().Add(d)
}

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

////////////////////////////////////////////////////////////////////////////////

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
	f.nudgeable = false
	time.Sleep(f.postBlinkWait)
	f.nudgeable = true
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
			if Abs(fBlink.fID-fOther.fID)%500 > 5 {
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
	// nF := 50
	nF := 500
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

	go nudger(fireflies, blinkCh)

	// wait a while
	time.Sleep(500 * time.Second)
	fmt.Println("Quit.")
}

func main() {
	fmt.Println("vim-go")

	// which := "single"
	// which := "ticker1"
	// which := "ticker2"
	which := "hatch"
	// which := "timediff"
	// which := "safetimer"
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
		blinkBlinkTimer()
	}
}

// https://golang.org/pkg/time/#Timer.Reset
// https://golang.org/pkg/time/#Ticker.Reset
