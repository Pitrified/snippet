package main

import (
	"image"
	"log"
	"time"

	"golang.org/x/exp/shiny/driver"
	"golang.org/x/exp/shiny/screen"
	"golang.org/x/mobile/event/key"
	"golang.org/x/mobile/event/paint"
)

type WrapImg struct {
	winSize image.Point
	w       screen.Window

	data chan int
}

func (wi WrapImg) Run() {
	driver.Main(func(s screen.Screen) {
		var err error

		wi.winSize = image.Point{900, 600}
		log.Printf("wi.winSize = %+v\n", wi.winSize)
		wi.w, err = s.NewWindow(&screen.NewWindowOptions{
			Width:  wi.winSize.X,
			Height: wi.winSize.Y,
			Title:  "Viewer",
		})
		if err != nil {
			log.Fatalf("s.NewWindow: %+v", err)
		}
		defer wi.w.Release()

		e := paint.Event{}
		log.Printf("Sending paint.Event inside Run : %T %+v", e, e)
		wi.w.Send(e)

		for {
			e := wi.w.NextEvent()
			switch e := e.(type) {

			default:

			case key.Event:
				switch e.Code {
				case key.CodeEscape, key.CodeQ:
					return
				}

			case paint.Event:
				log.Printf("Received paint.Event: %T %+v", e, e)
				// also this is a problem, as paint events are generated by other sources
				// log.Printf("wi.data = %+v\n", <-wi.data)

			case error:
				log.Print(e)

			}
		}

	})
}

// func (wi WrapImg) wFill() {
// 	log.Printf("wi.winSize = %+v\n", wi.winSize)
// 	wi.w.Fill(image.Rectangle{image.Point{}, wi.winSize},
// 		color.RGBA{30, 30, 30, 255}, draw.Src)
// }

func (wi WrapImg) sendPaint(data int) {

	log.Printf("inside sendPaint : wi.winSize = %+v\n", wi.winSize)

	e := paint.Event{}
	log.Printf("Sending paint.Event inside sendPaint : %T %+v", e, e)
	wi.w.Send(e)

	// log.Printf("Putting data on ch")
	// wi.data <- data
}

func wrapImg() {
	// create an object that runs the GUI

	dataCh := make(chan int)

	// create the wrapper to hold the image and the Window
	myWI := WrapImg{data: dataCh}

	// initialize the window inside
	go myWI.Run()

	time.Sleep(3 * time.Second)

	// send an event with the window
	log.Printf("Starting sendPaint")
	myWI.sendPaint(10)

	time.Sleep(time.Second)

	// myWI.wFill()
}
