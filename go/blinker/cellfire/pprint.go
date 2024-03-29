package cellfire

import "fmt"

var chPrint chan string

// A fancy printer to write one dot every N blinks.
func PrinterInit(ratio int) {
	chPrint = make(chan string, 1000)
	go Printer(ratio)
}

func Printer(ratio int) {
	i := 0
	for p := range chPrint {
		if p == "." {
			i++
			if i == ratio {
				i = 0
				fmt.Print(p)
			}
		} else {
			fmt.Print(p)
		}
	}
}
