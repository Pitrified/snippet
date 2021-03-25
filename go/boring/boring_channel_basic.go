package main

import (
	"fmt"
	"math/rand"
	"time"
)

// https://talks.golang.org/2012/concurrency.slide#20

// When the main function executes <–c, it will wait for a value to be sent.
// Similarly, when the boring function executes c <– value, it waits for a
// receiver to be ready.
// A sender and receiver must both be ready to play their part in the
// communication. Otherwise we wait until they are.
// Thus channels both communicate and synchronize.

func sample_channel_basic() {
	c := make(chan string)
	go boring_channel_basic("Boring channel basic", c)
	for i := 0; i < 5; i++ {
		// Receive expression is just a value.
		fmt.Println("Sample waiting for value.")
		fmt.Printf("You say: %q\n", <-c)
	}
	fmt.Println("You're boring; I'm leaving.")
}

func boring_channel_basic(msg string, c chan string) {
	for i := 0; ; i++ {
		// Expression to be sent can be any suitable value.
		fmt.Println("   Boring putting value.")
		c <- fmt.Sprintf("%s v %d", msg, i)
		fmt.Println("   Boring putting another value.")
		c <- fmt.Sprintf("%s a %d", msg, i)
		fmt.Println("   Boring done another value.")
		time.Sleep(time.Duration(rand.Intn(1e3)) * time.Millisecond)
	}
}
