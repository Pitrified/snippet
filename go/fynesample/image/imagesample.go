package main

import (
	"fmt"
	"image"
	"log"
	"os"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
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
	img, format, err := getImageFromFilePath("hilbert.png")
	if err != nil {
		log.Fatalln(err)
	}
	log.Println("Decoded format", format)

	// cImg := canvas.NewImageFromImage(img)
	cImg := &canvas.Image{}

	// cImg.FillMode = canvas.ImageFillOriginal
	cImg.FillMode = canvas.ImageFillContain

	cImg.ScaleMode = canvas.ImageScalePixels

	cImg.Image = img

	// allBlack := canvas.NewRectangle(color.Black)
	// imageBorder := container.New(layout.NewBorderLayout(nil, nil, nil, nil), allBlack, cImg)
	// imageWrap := container.NewGridWrap(fyne.NewSize(600, 600), imageBorder)

	// imageWrap := container.NewGridWrap(fyne.NewSize(600, 600), cImg)

	// imageFix := container.NewWithoutLayout(cImg)
	// cImg.Resize(fyne.NewSize(600, 600))
	// cImg.Move(fyne.NewPos(100, 100))
	// imageFix.Resize(fyne.NewSize(400, 400))
	// imageFix.Move(fyne.NewPos(100, 100))

	// imageWrap := container.NewGridWrap(fyne.NewSize(600, 600), imageFix)

	imageCenter := container.NewCenter(cImg)

	hcont := container.NewVBox(
		widget.NewLabel("Over"),
		// cImg,
		// imageBorder,
		// imageWrap,
		// imageFix,
		imageCenter,
		widget.NewLabel("Under"),
	)

	// win.SetContent(cImg)
	win.SetContent(hcont)

	win.Resize(fyne.NewSize(1200, 1200))
	win.Show()
	app.Run()
}
