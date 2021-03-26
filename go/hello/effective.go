package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"sort"
	"time"
)

type ByteSize float64

const (
	_           = iota // ignore first value by assigning to blank identifier
	KB ByteSize = 1 << (10 * iota)
	MB
	GB
	TB
	PB
	EB
	ZB
	YB
)

func (b ByteSize) String() string {
	switch {
	case b >= YB:
		return fmt.Sprintf("%.2fYB", b/YB)
	case b >= ZB:
		return fmt.Sprintf("%.2fZB", b/ZB)
	case b >= EB:
		return fmt.Sprintf("%.2fEB", b/EB)
	case b >= PB:
		return fmt.Sprintf("%.2fPB", b/PB)
	case b >= TB:
		return fmt.Sprintf("%.2fTB", b/TB)
	case b >= GB:
		return fmt.Sprintf("%.2fGB", b/GB)
	case b >= MB:
		return fmt.Sprintf("%.2fMB", b/MB)
	case b >= KB:
		return fmt.Sprintf("%.2fKB", b/KB)
	}
	return fmt.Sprintf("%.2fB", b)
}

// https://golang.org/doc/effective_go#constants
func effectiveConstant() {
	tb := ByteSize(1e13)
	fmt.Println("1e13", tb)
	fmt.Println("TB", TB)
}

var (
	home   = os.Getenv("HOME")
	user   = os.Getenv("USER")
	gopath = os.Getenv("GOPATH")
)

// Finally, each source file can define its own niladic init function to set
// up whatever state is required. (Actually each file can have multiple init
// functions.) And finally means finally: init is called after all the
// variable declarations in the package have evaluated their initializers,
// and those are evaluated only after all the imported packages have been
// initialized.
func init() {
	if user == "" {
		log.Fatal("$USER not set")
	}
	if home == "" {
		home = "/home/" + user
	}
	if gopath == "" {
		gopath = home + "/go"
	}
	// gopath may be overridden by --gopath flag on command line.
	flag.StringVar(&gopath, "gopath", gopath, "override default GOPATH")
}

// https://golang.org/doc/effective_go#init
func effectiveInit() {
	fmt.Printf("user, home, gopath = %+v %+v %+v\n", user, home, gopath)
}

var _ = fmt.Printf // For debugging; delete when done.
var _ io.Reader    // For debugging; delete when done.

func effectiveBlank() {
	fd, err := os.Open("hello.go")
	if err != nil {
		log.Fatal(err)
	}
	// TODO: use fd.
	_ = fd
}

// https://golang.org/doc/effective_go#channels
func effectiveChannels() {
	islice := []int{5, 3, 4, 9, 1, 6, 2, 7, 4, 7}
	c := make(chan int) // Allocate a channel.
	// Start the sort in a goroutine; when it completes, signal on the channel.
	go func() {
		islice = sort.IntSlice(islice)
		c <- 1 // Send a signal; value does not matter.
	}()
	start := time.Now()
	<-c // Wait for sort to finish; discard sent value.
	fmt.Println("Waited for", time.Since(start))
	fmt.Println("Sorted", islice)

}
