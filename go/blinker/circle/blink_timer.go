package circle

import "time"

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
