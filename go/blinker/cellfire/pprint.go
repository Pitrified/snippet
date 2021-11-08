package cellfire

import "fmt"

var chPrint chan string

// A fancy printer to write one dot every N blinks.
func Printer() {
	chPrint = make(chan string, 1000)
	i := 0
	for p := range chPrint {
		if p == "." {
			i++
			if i == 10 {
				i = 0
				fmt.Print(p)
			}
		} else {
			fmt.Print(p)
		}
	}
}
