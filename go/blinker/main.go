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

// generate blinks every 0.8-1.2 sec
// after 1 sec blink anyway
// if the blink is forced, stop the other timer
func blinkTicker2() {
	rand.Seed(time.Now().UnixNano())

	ticker := time.NewTicker(time.Second)
	timer := time.NewTimer(randDuration(0.8, 0.4))

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

			// if !timer.Stop() {
			// 	fmt.Println("Stopping timer.")
			// 	<-timer.C
			// }
			// timer.Reset(randDuration(0.8, 0.4))

			timer = time.NewTimer(randDuration(0.8, 0.4))

		case t := <-timer.C:
			fmt.Println("Timer : ", t)
			// reset the ticker
			ticker.Reset(time.Second)
		}
	}
}

// struct that holds the end
// when nudged, compute the new end
// check if newEnd.before(Now)
// true: blink, reset ticker
// false: nothing
// each struct is created and then golaunched

type Firefly struct {
	ticker    *time.Ticker
	nextBlink time.Time
	period    time.Duration

	nudgeCh chan bool
	blinkCh chan<- *Firefly

	fID int
}

func (f *Firefly) blinker() {
	for {
		select {

		// move nextBlink in the past proportionally to the distance to that instant
		// if it is now in the past, blink and reset the ticker
		case <-f.nudgeCh:
			fmt.Printf("Nudged %d.\n", f.fID)

		// blink
		case t := <-f.ticker.C:
			fmt.Printf("Ticked %d at: %v\n", f.fID, t)
			f.blinkCh <- f
		}
	}
}

func nudger(fireflies map[int]*Firefly, blinkCh <-chan *Firefly) {
	for {
		// this Firefly just blinked
		f := <-blinkCh
		for fID, firefly := range fireflies {
			// skip the current firefly
			if f.fID == fID {
				continue
			}
			// nudge the others
			firefly.nudgeCh <- true
		}
	}

}

func hatch() {
	// the swarm
	fireflies := make(map[int]*Firefly)
	nF := 10
	// the channel where each firefly sends a bool when blinking
	blinkCh := make(chan *Firefly)
	for i := 0; i < nF; i++ {
		// blinking period
		period := randDuration(0.9, 0.2)
		ticker := time.NewTicker(period)
		nextBlink := time.Now().Add(period)
		// each firefly can be nudged independently
		nudgeCh := make(chan bool)
		fireflies[i] = &Firefly{
			ticker,
			nextBlink,
			period,
			nudgeCh,
			blinkCh,
			i,
		}
		go fireflies[i].blinker()
	}

	go nudger(fireflies, blinkCh)

	// should probably wait somewhere
	time.Sleep(5 * time.Second)
}

func main() {
	fmt.Println("vim-go")

	// which := "single"
	// which := "ticker1"
	// which := "ticker2"
	which := "hatch"
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
	}
}

// https://golang.org/pkg/time/#Timer.Reset
// https://golang.org/pkg/time/#Ticker.Reset
