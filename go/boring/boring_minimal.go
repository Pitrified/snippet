package main

import (
	"fmt"
	"math/rand"
	"time"
)

// https://talks.golang.org/2012/concurrency.slide#16
func sample_boring_minimal() {
	go boring_minimal("Boring minimal")
	fmt.Println("I'm listening.")
	time.Sleep(2 * time.Second)
	fmt.Println("You're boring; I'm leaving.")
}

func boring_minimal(msg string) {
	for i := 0; ; i++ {
		fmt.Println(msg, i)
		time.Sleep(time.Duration(rand.Intn(1e3)) * time.Millisecond)
	}
}
