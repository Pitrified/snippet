package main

import (
	"fmt"
	"math/rand"
	"time"
)

// https://talks.golang.org/2012/concurrency.slide#25

// Channels as a handle on a service
// Our boring function returns a channel that lets us communicate with the
// boring service it provides.
// We can have more instances of the service.

func sample_boring_generator_1() {
	// Function returning a channel.
	c := boring_generator("Boring generator")
	for i := 0; i < 5; i++ {
		fmt.Printf("You say: %q\n", <-c)
	}
	fmt.Println("You're boring; I'm leaving.")
}

// These programs make Joe and Ann count in lockstep.
func sample_boring_generator_2() {
	alice := boring_generator("Alice: ")
	bob := boring_generator("Bob:   ")
	for i := 0; i < 5; i++ {
		fmt.Println(<-alice)
		fmt.Println(<-bob)
	}
	fmt.Println("You're boring; I'm leaving.")
}

func fanInF(input1, input2 <-chan string) <-chan string {
	c := make(chan string)
	go func() {
		for {
			c <- <-input1
		}
	}()
	go func() {
		for {
			c <- <-input2
		}
	}()
	return c
}

func sample_boring_generator_3() {
	rand.Seed(time.Now().UnixNano())
	c := fanInF(boring_generator("Alice"), boring_generator("Bob"))
	for i := 0; i < 10; i++ {
		fmt.Println(<-c)
	}
	fmt.Println("You're all boring; I'm leaving.")
}

// tricky error: if the closures are linked to the for variables
// by the time those are launched all closures use the same var
// note how *i* is the same, *fi* changes
func fanInV(inputs ...<-chan string) <-chan string {
	c := make(chan string)
	for i, ch := range inputs {
		fi := i
		fch := ch
		// here i and fi have the same value
		fmt.Println("Adding channel", i, fi)
		go func() {
			// here i has the last value, fi has the correct value
			fmt.Println("Go func channel", i, fi)
			for {
				c <- <-fch
			}
		}()
	}
	return c
}

func sample_boring_generator_4() {
	rand.Seed(time.Now().UnixNano())
	c := fanInV(boring_generator("Alice"), boring_generator("Bob"))
	for i := 0; i < 10; i++ {
		fmt.Println(<-c)
	}
	fmt.Println("You're all boring; I'm leaving.")
}

// identical to fanInV but with slices
func fanInS(inputs []<-chan string) <-chan string {
	c := make(chan string)
	for i := range inputs {
		fi := i
		fmt.Println("Adding channel", i, fi)
		go func() {
			fmt.Println("Go func channel", i, fi)
			for {
				c <- <-inputs[fi]
			}
		}()
	}
	return c
}

func sample_boring_generator_5() {
	rand.Seed(time.Now().UnixNano())
	cn := 4
	cs := make([]<-chan string, cn)
	for i := 0; i < cn; i++ {
		cs[i] = boring_generator(fmt.Sprintf("Ch %d", i))
	}
	c := fanInS(cs)
	for i := 0; i < 5*cn; i++ {
		fmt.Println(<-c)
	}
	fmt.Println("You're all boring; I'm leaving.")
}

// Returns receive-only channel of strings.
func boring_generator(msg string) <-chan string {
	c := make(chan string)
	// We launch the goroutine from inside the function.
	go func() {
		fmt.Println("Starting generator", msg)
		for i := 0; ; i++ {
			c <- fmt.Sprintf("%s %d", msg, i)
			time.Sleep(time.Duration(rand.Intn(1e3)) * time.Millisecond)
		}
	}()
	// Return the channel to the caller.
	return c
}

// n4aew
