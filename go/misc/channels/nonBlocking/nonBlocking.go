package main

import (
	"fmt"
	"time"
)

func fill(messages chan string) {
	fmt.Printf("Filling the channel.\n")
	messages <- "Filled."
}

func main() {
	fmt.Println("vim-go")

	messages := make(chan string)

	go fill(messages)

	time.Sleep(100 * time.Millisecond)

	select {
	case messages <- "Filling.":
	default:
		fmt.Printf("Channel was full.\n")
	}
}
