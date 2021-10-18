package main

import (
	"image"
	"image/color"
	"image/draw"
	"log"
	"time"

	"golang.org/x/exp/shiny/driver"
	"golang.org/x/exp/shiny/screen"
	"golang.org/x/mobile/event/key"
	"golang.org/x/mobile/event/paint"
	"golang.org/x/mobile/event/size"
)

func sendEvent(w screen.Window, dataCh chan uint8) {

	time.Sleep(3 * time.Second)
	log.Printf("Imma send the event now")

	// put data on the channel
	dataCh <- 80

	// notify the main loop that there is data
	e := paint.Event{}
	log.Printf("Sending paint.Event inside sendEvent : %T %+v", e, e)
	w.Send(e)
}

func embedImg() {

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

		// // color inside the Window
		// v := uint8(100)
		// w.Fill(image.Rectangle{image.Point{}, winSize}, color.RGBA{v, v, v, 255}, draw.Src)
		// // maybe it is needed?
		// pr := w.Publish()
		// log.Printf("w.Publish: %T %+v", pr, pr)
		// // at this point I still see a black window

		// create a Buffer
		size0 := image.Point{30, 30}
		b, err := s.NewBuffer(size0)
		if err != nil {
			log.Fatalf("s.NewBuffer: %+v", err)
		}
		defer b.Release()

		// create a channel where sendEvent will put data
		// not single so that it does not block
		dataCh := make(chan uint8, 2)

		go sendEvent(w, dataCh)

		var sz size.Event
		for {
			e := w.NextEvent()
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

				select {

				case v1 := <-dataCh:
					log.Printf("Received data on channel : %T %+v", v1, v1)
					w.Fill(sz.Bounds(), color.RGBA{v1, v1, v1, 255}, draw.Src)

				default:
					log.Printf("Received no data on channel")

				}

			case size.Event:
				sz = e
				// fill the Window with some gray
				w.Fill(sz.Bounds(), color.RGBA{80, 80, 80, 255}, draw.Src)
				// upload the black buffer on the window
				w.Upload(image.Point{30, 30}, b, b.Bounds())

			case error:
				log.Print(e)

			}
		}

	})

}