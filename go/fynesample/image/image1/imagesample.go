package main

import (
	"fmt"
	"image"
	"image/color"
	"log"
	"os"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"
)

// https://stackoverflow.com/a/49595208/2237151
func getImageFromFilePath(filePath string) (image.Image, string, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return nil, "", err
	}
	defer f.Close()
	m, format, err := image.Decode(f)
	return m, format, err
}

func main() {
	fmt.Println("vim-go")

	app := app.New()
	win := app.NewWindow("Image test")

	// img, format, err := getImageFromFilePath("small.png")
	img, format, err := getImageFromFilePath("../hilbert.png")
	if err != nil {
		log.Fatalln(err)
	}
	log.Println("Decoded format", format)

	cImg := canvas.NewImageFromImage(img)
	cImg.FillMode = canvas.ImageFillContain
	cImg.ScaleMode = canvas.ImageScaleFastest
	// not strictly necessary, but in the beginning the canvas appears as small as possible,
	// so we force it to appear; if you do win.Resize(fyne.NewSize(1200, 1200)) it is redundant,
	// but it is still prettier to leave a MinSize (for when the user resizes the app)
	cImg.SetMinSize(fyne.NewSize(200, 200))

	// a background to show the size that could potentially be filled
	allBlack := canvas.NewRectangle(color.RGBA{30, 30, 30, 255})
	// border magically tells the widgets inside to be as big as possible:
	// allBlack will grow as needed
	imageBorder := container.New(layout.NewBorderLayout(nil, nil, nil, nil), allBlack, cImg)

	// sample content
	over := widget.NewLabel("Over")
	under := widget.NewLabel("Under")
	// allow the image to grow
	borderCont := container.New(layout.NewBorderLayout(over, under, nil, nil),
		over, under, imageBorder)

	// set the content
	win.SetContent(borderCont)

	// win.Resize(fyne.NewSize(1200, 1200))
	win.Show()
	app.Run()
}
