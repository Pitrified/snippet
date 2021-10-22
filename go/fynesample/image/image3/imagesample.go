package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"log"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"
)

// raster generator func
func rasterUpdate(w, h int) image.Image {
	fmt.Printf("rasterUpdate : w, h = %+v %+v\n", w, h)
	pixW := w
	pixH := h
	img := image.NewRGBA(image.Rect(0, 0, pixW, pixH))
	draw.Draw(img, img.Bounds(), &image.Uniform{color.RGBA{10, 10, 10, 255}}, image.Point{0, 0}, draw.Src)
	return img
}

func main() {
	fmt.Println("vim-go")

	myApp := app.New()
	w := myApp.NewWindow("Image test")

	raster := canvas.NewRaster(rasterUpdate)
	raster.SetMinSize(fyne.NewSize(600, 600))

	text1 := canvas.NewText("Hello", color.White)
	text2 := canvas.NewText("There", color.RGBA{150, 75, 0, 255})
	text3 := canvas.NewText("(right)", color.White)
	contentTop := container.New(layout.NewHBoxLayout(), text1, text2, layout.NewSpacer(), text3)

	input := widget.NewEntry()
	input.SetPlaceHolder("Enter text...")
	inp_content := container.NewVBox(input, widget.NewButton("Save", func() {
		log.Println("Content was:", input.Text)
	}))

	borderCont := container.New(layout.NewBorderLayout(contentTop, inp_content, nil, nil),
		contentTop, inp_content, raster)

	w.SetContent(borderCont)

	w.Resize(fyne.NewSize(1200, 1200))

	w.Show()
	myApp.Run()
}
