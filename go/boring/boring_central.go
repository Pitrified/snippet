package main

import (
	"fmt"
)

// examples from https://talks.golang.org/2012/concurrency.slide#6

// Concurrency is the composition of independently executing computations.

// A goroutine is an independently executing function,
// launched by a go statement.
// It has its own call stack, which grows and shrinks as required.

func main() {
	fmt.Println("vim-go")

	// which := "minimal"
	// which := "channel_basic"
	// which := "generator1"
	// which := "generator2"
	// which := "generator3"
	// which := "generator4"
	which := "generator5"
	fmt.Printf("which = %+v\n", which)

	switch which {
	case "minimal":
		sample_boring_minimal()
	case "channel_basic":
		sample_channel_basic()
	case "generator1":
		sample_boring_generator_1()
	case "generator2":
		sample_boring_generator_2()
	case "generator3":
		sample_boring_generator_3()
	case "generator4":
		sample_boring_generator_4()
	case "generator5":
		sample_boring_generator_5()
	}
}
