package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"time"
)

type AnnotatedTime struct {
	now time.Time
	wID int
}

func (at *AnnotatedTime) String() string {
	return fmt.Sprintf("%v,%v", at.now.UnixNano(), at.wID)
}

func centralWriter(input <-chan interface{}, done chan bool) {
	f, err := os.Create("output_write_multi_500_buffer0_16.txt")
	check(err)
	defer f.Close()

	w := bufio.NewWriter(f)
	fmt.Printf("w.Size() = %+v\n", w.Size())
	w = bufio.NewWriterSize(w, 4096*16)
	fmt.Printf("w.Size() = %+v\n", w.Size())

	for {
		select {
		case val := <-input:
			strVal := fmt.Sprintf("%v\n", val)
			// fmt.Print(strVal)
			_, err := w.WriteString(strVal)
			check(err)
		case <-done:
			w.Flush()
			done <- true
			return
		}
	}
}

func worker(output chan<- interface{}, done chan bool, wID int) {
	var totalTime int64 = 0
	totalLoops := 0
	for {
		select {
		case <-time.After(time.Duration((0.2 + rand.Float64()*0.4) * 1e9)):
			start := time.Now()
			output <- &AnnotatedTime{time.Now(), wID}
			diff := time.Since(start)
			totalTime += diff.Nanoseconds()
			totalLoops++
		case <-done:
			meanWait := float64(totalTime) / float64(totalLoops)
			// fmt.Printf("Closed %v with meanWait = %v\n", wID, meanWait)
			// output <- fmt.Sprintf("%v,%v", meanWait, wID)
			output <- fmt.Sprintf("+%v", int(meanWait))
			return
		}
	}
}

func sampleCentralWrite() {
	// setup channels
	c := make(chan interface{})
	// c := make(chan interface{}, 100000)
	doneWorker := make(chan bool)
	doneWriter := make(chan bool)

	numWorkers := 500

	// start workers
	for i := 0; i < numWorkers; i++ {
		go worker(c, doneWorker, i)
	}
	// start writer
	go centralWriter(c, doneWriter)

	// wait a bit
	time.Sleep(1 * time.Second)

	// stop all workers (will write recap on writerchannel)
	for i := 0; i < numWorkers; i++ {
		doneWorker <- true
	}

	// give time to write result lol so bad use a WaitGroup I guess?
	time.Sleep(1 * time.Second)

	// close the writer
	doneWriter <- true
	<-doneWriter
}

// total output_write_multi_50k_buffer0k.txt              7,056,605,842
// total output_write_multi_50k_buffer1k.txt                871,685,894
// total output_write_multi_50k_buffer10k.txt               376,205,783
// total output_write_multi_500k_buffer0k.txt       219,207,622,250,785
// total output_write_multi_500k_buffer0k_16.txt    200,258,398,938,107
// total output_write_multi_500k_buffer1k.txt       215,859,513,370,059
// total output_write_multi_500k_buffer10k.txt      210,062,267,867,756
// total output_write_multi_500k_buffer100k.txt     185,410,048,245,641
// total output_write_multi_500k_buffer100k_16.txt  184,574,371,102,375
