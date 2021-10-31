package circle

import (
	"bufio"
	"fmt"
	"os"
	"time"

	"blinker/utils"
)

// prints all the strings received on input channel
// every second prints a newline
func centralPrinter(input <-chan string, done chan bool) {

	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()

	count := 0

	for {
		select {

		case val := <-input:
			fmt.Print(val)

		case <-ticker.C:
			fmt.Println(count)
			count++

		case <-done:
			return
		}
	}
}

// write the string as is on the file
func centralWriter(input <-chan string, done chan bool, fileName string) {
	f, err := os.Create(fileName)
	if err != nil {
		// panic(err)
		// just drain the channel forever
		for {
			select {
			case <-input:
			case <-done:
				done <- true
				return
			}
		}
	}
	defer f.Close()

	// create a buffered writer
	w := bufio.NewWriter(f)

	// a ticker to flush sometimes (to stop the run early and have some data)
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	count := 0

	for {
		select {

		// write the received value
		case val := <-input:
			_, err := w.WriteString(val)
			utils.Check(err)
			count++

		// flush every period
		case <-ticker.C:
			w.Flush()
			fmt.Printf("count = %v\n", count)
			count = 0

		// flush the buffer when closing
		case <-done:
			w.Flush()
			done <- true
			return
		}
	}
}
