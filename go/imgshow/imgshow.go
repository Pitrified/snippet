package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"log"
	"math/rand"

	"golang.org/x/exp/shiny/driver"
	"golang.org/x/exp/shiny/screen"
	"golang.org/x/mobile/event/key"
	"golang.org/x/mobile/event/lifecycle"
	"golang.org/x/mobile/event/mouse"
	"golang.org/x/mobile/event/paint"
	"golang.org/x/mobile/event/size"
)

func runAppBis(s screen.Screen) {
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
	size0 := image.Point{30, 30}
	b, err := s.NewBuffer(size0)
	if err != nil {
		log.Fatalf("s.NewBuffer: %+v", err)
	}
	defer b.Release()

	// fill it with a color
	white := color.RGBA{255, 255, 255, 255}
	draw.Draw(b.RGBA(), b.RGBA().Bounds(), &image.Uniform{white}, image.Point{0, 0}, draw.Src)

	// draw it on the window
	w.Upload(image.Point{30, 30}, b, b.Bounds())

	v := uint8(100)
	w.Fill(image.Rectangle{image.Point{}, winSize}, color.RGBA{v, v, v, 255}, draw.Src)

	pr := w.Publish()
	log.Printf("w.Publish: %T %+v", pr, pr)

	// at this point I see a black window

	var sz size.Event
	for {
		e := w.NextEvent()
		switch e := e.(type) {

		default:

		case key.Event:
			if e.Code == key.CodeEscape {
				return
			}

		case mouse.Event:
			v := uint8(rand.Intn(255))
			w.Fill(image.Rectangle{image.Point{}, winSize}, color.RGBA{v, v, v, 255}, draw.Src)
			w.Upload(image.Point{30, 30}, b, b.Bounds())

		case size.Event:
			sz = e
			w.Fill(sz.Bounds(), color.RGBA{80, 80, 80, 255}, draw.Src)
			w.Upload(image.Point{30, 30}, b, b.Bounds())

		case paint.Event:
			log.Printf("paint.Event: %T %+v", e, e)
		}
	}
}

func runApp(s screen.Screen) {

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
	size0 := image.Point{30, 30}
	b, err := s.NewBuffer(size0)
	if err != nil {
		log.Fatalf("s.NewBuffer: %+v", err)
	}
	defer b.Release()
	white := color.RGBA{255, 255, 255, 255}
	// b.RGBA().Set(0, 1, white)
	// b.RGBA().Set(2, 1, white)
	// b.RGBA().Set(1, 0, white)
	// b.RGBA().Set(1, 2, white)

	// draw.Draw(img, img.Bounds(), &image.Uniform{SoftBlack}, image.Point{0, 0}, draw.Src)
	draw.Draw(b.RGBA(), b.RGBA().Bounds(), &image.Uniform{white}, image.Point{0, 0}, draw.Src)

	t, err := s.NewTexture(size0)
	if err != nil {
		log.Fatal(err)
	}
	defer t.Release()
	t.Upload(image.Point{}, b, b.Bounds())
	// t.Fill(t.Bounds(), white, draw.Src)

	// w.Fill(image.Rectangle{image.Point{}, winSize}, color.RGBA{10, 10, 10, 255}, draw.Src)
	w.Fill(image.Rectangle{image.Point{}, winSize}, color.RGBA{80, 80, 80, 255}, draw.Src)

	w.Copy(image.Point{10, 10}, t, t.Bounds(), draw.Src, nil)
	// w.Copy(image.Point{10, 10}, t, t.Bounds(), draw.Over, nil)
	// Copy copies the sub-Texture defined by src and sr to the destination
	// (the method receiver), such that sr.Min in src-space aligns with dp in
	// dst-space.

	w.Upload(image.Point{40, 40}, b, b.Bounds())
	// fmt.Printf("b.RGBA().Pix = %T %+v\n", b.RGBA().Pix, b.RGBA().Pix)
	fmt.Printf("w = %+v\n", w)
	// w.Publish()

	// time.Sleep(time.Second)

	var sz size.Event
	for {
		e := w.NextEvent()
		switch e := e.(type) {

		default:
			log.Printf("Unknown w.NextEvent: %T %+v", e, e)

		case lifecycle.Event:
			log.Printf("lifecycle.Event: %T %+v", e, e)
			if e.To == lifecycle.StageDead {
				return
			}

		case key.Event:
			log.Printf("key.Event: %T %+v", e, e)

			switch e.Code {

			default:

			case key.CodeEscape, key.CodeQ:
				return

			}

		case mouse.Event:
			// movement
			if e.Direction == mouse.DirNone {
				break
			}
			log.Printf("mouse.Event: %T %+v", e, e)
			// log.Printf("           : %T %+v", e.Direction, e.Direction)
			v := uint8(rand.Intn(255))
			w.Fill(image.Rectangle{image.Point{}, winSize}, color.RGBA{v, v, v, 255}, draw.Src)

		case size.Event:
			sz = e
			log.Printf("size.Event: %+v", sz)
			w.Fill(sz.Bounds(), color.RGBA{80, 80, 80, 255}, draw.Src)
			// w.Fill(sz.Bounds(), color.RGBA{10, 10, 10, 255}, draw.Src)

			w.Copy(image.Point{10, 10}, t, t.Bounds(), draw.Src, nil)
			w.Upload(image.Point{30, 30}, b, b.Bounds())

		case paint.Event:
			log.Printf("paint.Event: %T %+v", e, e)

		case error:
			log.Printf("error @ w.NextEvent: %+v", e)

		}
	}
}

func main() {
	fmt.Println("vim-go")

	// some weird things are happening with the update/publish
	// https://stackoverflow.com/questions/66994242/publishing-changes-to-window-with-shiny-driver

	driver.Main(runAppBis)

	fmt.Println("vim-go-app")
	driver.Main(runApp)
}
