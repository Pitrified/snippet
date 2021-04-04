package main

import (
	"fmt"
)

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
