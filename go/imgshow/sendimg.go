package main

import (
	"image"
	"image/color"
	"image/draw"
	"log"
	"math/rand"
	"time"

	"golang.org/x/exp/shiny/driver"
	"golang.org/x/exp/shiny/screen"
	"golang.org/x/mobile/event/key"
	"golang.org/x/mobile/event/paint"
	"golang.org/x/mobile/event/size"
)

func imgCreate(c chan<- int) {
	// create images and send them on the channel

	N := 4
	for i := 0; i < N; i++ {
		time.Sleep(time.Duration(rand.Intn(1e3)) * time.Millisecond)
		c <- i
	}
	close(c)
}

func imgPaint(c <-chan int) {
	// receive images and paint them on the window

	// for v1 := range c {
	// 	fmt.Printf("v1 = %+v\n", v1)
	// }

	driver.Main(func(s screen.Screen) {
		// create a Window
		winSize := image.Point{900, 600}
		w, err := s.NewWindow(&screen.NewWindowOptions{
			Width:  winSize.X,
			Height: winSize.Y,
			Title:  "Viewer",
		})
		if err != nil {
			log.Fatalf("s.NewWindow: %+v", err)
		}
		defer w.Release()

		// create a Buffer
		// size0 := image.Point{30, 30}
		b, err := s.NewBuffer(winSize)
		if err != nil {
			log.Fatalf("s.NewBuffer: %+v", err)
		}
		defer b.Release()

		w.Fill(b.Bounds(), color.White, draw.Src)
		w.Publish()

		// MAYBE start here imgCreate so you can pass w as arg and that can
		// call w.send(paint.Event{})

		time.Sleep(time.Second)

		for {
			e := w.NextEvent()
			switch e := e.(type) {

			default:

			case key.Event:
				switch e.Code {
				case key.CodeEscape:
					return
				case key.CodeR:
					if e.Direction == key.DirPress {
						log.Println("Sending paint event.")
						w.Send(paint.Event{})
					}
				case key.CodeC:
					if e.Direction == key.DirPress {
						v := uint8(rand.Intn(255))
						log.Println("Filling with color.")
						w.Fill(image.Rectangle{image.Point{}, winSize},
							color.RGBA{v, v, v, 255}, draw.Src)
					}
				}

			case paint.Event:
				log.Printf("paint.Event: %T %+v", e, e)

			case size.Event:
				log.Printf("size.Event: %T %+v", e, e)

			case error:
				log.Print(e)

			}
		}
	})
}

func sendImg() {
	// start 1 goroutine that creates images and the func that paints them

	c := make(chan int)

	go imgCreate(c)

	imgPaint(c)
}
