package main

import (
	"fmt"
	"image"
	"log"
	"os"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
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

type scrollImgRenderer struct {
	// img *image.RGBA
	img     *canvas.Image
	objects []fyne.CanvasObject
}

func (sir *scrollImgRenderer) MinSize() fyne.Size {
	return sir.img.MinSize()
}

func (sir *scrollImgRenderer) Layout(size fyne.Size) {
	sir.img.Resize(size)
}

func (sir *scrollImgRenderer) Refresh() {
	canvas.Refresh(sir.img)
}

func (sir *scrollImgRenderer) Objects() []fyne.CanvasObject {
	return sir.objects
}

func (sir *scrollImgRenderer) Destroy() {
}

type scrollImg struct {
	widget.BaseWidget
}

func (si *scrollImg) CreateRenderer() fyne.WidgetRenderer {
	sir := &scrollImgRenderer{}
	sir.img = &canvas.Image{}

	img, format, err := getImageFromFilePath("hilbert.png")
	if err != nil {
		log.Fatalln(err)
	}
	log.Println("Decoded format", format)

	sir.img.Image = img

	sir.objects = []fyne.CanvasObject{sir.img}
	return sir
}

func newScrollImg() *scrollImg {
	si := &scrollImg{}
	si.ExtendBaseWidget(si)
	return si
}

func main() {
	fmt.Println("vim-go")

	app := app.New()
	win := app.NewWindow("Image test")

	si := newScrollImg()

	win.SetContent(si)

	win.Resize(fyne.NewSize(1200, 1200))
	win.Show()
	app.Run()
}
