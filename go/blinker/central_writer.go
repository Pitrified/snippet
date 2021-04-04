package main

import (
	"fmt"
	"time"
)

// prints all the strings received on input channel
// every second prints a newline
func centralPrinter(input <-chan string, done chan bool) {

	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()

	for {
		select {

		case val := <-input:
			fmt.Print(val)

		case <-ticker.C:
			fmt.Println()

		case <-done:
			return
		}
	}
}
