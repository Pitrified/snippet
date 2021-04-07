package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"log"

	"golang.org/x/exp/shiny/driver"
	"golang.org/x/exp/shiny/screen"
	"golang.org/x/mobile/event/key"
	"golang.org/x/mobile/event/size"
)

func runApp(s screen.Screen) {

	// create a Window
	winSize := image.Point{900, 600}
	w, err := s.NewWindow(&screen.NewWindowOptions{
		Width:  winSize.X,
		Height: winSize.Y,
		Title:  "Title of the window",
	})
	if err != nil {
		log.Fatalf("s.NewWindow: %v", err)
	}
	defer w.Release()

	// create a Buffer
	b, err := s.NewBuffer(winSize)
	if err != nil {
		log.Fatalf("s.NewBuffer: %v", err)
	}
	defer b.Release()

	w.Fill(b.Bounds(), color.RGBA{10, 10, 10, 255}, draw.Src)
	w.Publish()

	var sz size.Event
	for {
		e := w.NextEvent()
		switch e := e.(type) {

		default:

		case key.Event:
			switch e.Code {

			default:

			case key.CodeEscape, key.CodeQ:
				return

			}

		case size.Event:
			sz = e
			log.Printf("size.Event: %v", sz)
			w.Fill(sz.Bounds(), color.RGBA{10, 10, 10, 255}, draw.Src)

		case error:
			log.Printf("w.NextEvent: %v", e)

		}
	}
}

func main() {
	fmt.Println("vim-go")

	driver.Main(runApp)
}
