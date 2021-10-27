package main

import (
	"fmt"
	"image"
	"log"
	"os"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/driver/desktop"
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
	img     *canvas.Image
	objects []fyne.CanvasObject

	si *scrollImg
}

var _ fyne.WidgetRenderer = &scrollImgRenderer{}

func (sir *scrollImgRenderer) MinSize() fyne.Size {
	return sir.img.MinSize()
}

func (sir *scrollImgRenderer) Layout(size fyne.Size) {
	fmt.Printf("Layout = %+v\n", size)
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

var _ fyne.Widget = &scrollImg{}

func (si *scrollImg) CreateRenderer() fyne.WidgetRenderer {
	sir := &scrollImgRenderer{}

	sir.si = si

	img, format, err := getImageFromFilePath("../hilbert.png")
	if err != nil {
		log.Fatalln(err)
	}
	log.Println("Decoded format", format)

	sir.img = &canvas.Image{}
	sir.img.Image = img
	sir.img.FillMode = canvas.ImageFillContain
	sir.img.ScaleMode = canvas.ImageScaleFastest
	sir.img.SetMinSize(fyne.Size{Width: 1200 / 2, Height: 1200 / 2})

	sir.objects = []fyne.CanvasObject{sir.img}

	return sir
}

// https://developer.fyne.io/api/v2.0/driver/desktop/mouseable.html
var _ desktop.Mouseable = &scrollImg{}

func (si *scrollImg) MouseDown(ev *desktop.MouseEvent) {
	fmt.Printf("MouseDown ev = %+v\n", ev)
}

func (si *scrollImg) MouseUp(ev *desktop.MouseEvent) {
	fmt.Printf("MouseUp ev = %+v\n", ev)
}

// https://developer.fyne.io/api/v2.0/driver/desktop/hoverable.html
var _ desktop.Hoverable = &scrollImg{}

func (si *scrollImg) MouseIn(ev *desktop.MouseEvent) {
	fmt.Printf("MouseIn ev = %+v\n", ev)
}

func (si *scrollImg) MouseMoved(ev *desktop.MouseEvent) {
	fmt.Printf("MouseMoved ev = %+v\n", ev)
}

func (si *scrollImg) MouseOut() {
	fmt.Print("MouseOut\n")
}

// https://developer.fyne.io/api/v2.0/scrollable.html
var _ fyne.Scrollable = &scrollImg{}

func (si *scrollImg) Scrolled(ev *fyne.ScrollEvent) {
	fmt.Printf("Scrolled ev = %+v\n", ev)
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
