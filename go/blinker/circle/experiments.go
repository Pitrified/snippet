package circle

import (
	"blinker/utils"
	"fmt"
	"math/rand"
	"time"
)

// https://golang.org/pkg/time/#Timer.Reset
// https://golang.org/pkg/time/#Ticker.Reset

////////////////////////////////////////////////////////////////////////////////

// sample use of a timeout
func BlinkTimeoutSingle() {
	rand.Seed(time.Now().UnixNano())

	ch := make(chan string)

	go utils.RandSleep(2, ch)

	select {
	case res := <-ch:
		fmt.Println("Got res: ", res)
	case <-time.After(1 * time.Second):
		fmt.Println("Timeout.")
	}
}

////////////////////////////////////////////////////////////////////////////////

// sample use of a ticker
func BlinkTicker1() {
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
func BlinkTicker2() {
	rand.Seed(time.Now().UnixNano())

	// begin := 0.8
	// length := 0.4

	// very close to 1s, to force the flush
	begin := 0.999
	length := 0.002

	ticker := time.NewTicker(time.Second)
	timer := time.NewTimer(utils.RandDuration(begin, length))

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
			timer.Reset(utils.RandDuration(begin, length))

		case t := <-timer.C:
			fmt.Println("Timer : ", t)
			// reset the ticker
			ticker.Reset(time.Second)
			// reset the timer as well to restart it
			timer.Reset(utils.RandDuration(begin, length))
		}
	}
}

////////////////////////////////////////////////////////////////////////////////

// test with manipulating time
func TimeDiff() {
	rand.Seed(time.Now().UnixNano())

	// setup some deadline
	now := time.Now()
	fmt.Printf("now         : %v %T\n", now, now)
	period := utils.RandDuration(0.9, 0.2)
	fmt.Printf("period      : %v %T\n", period, period)
	nextBlink := time.Now().Add(period)
	fmt.Printf("nextBlink   : %v %T\n", nextBlink, nextBlink)

	// sleep for a while
	sleep := utils.RandDuration(0.1, 0.1)
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
