package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/driver/desktop"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"
)

// --------------------------------------------------------------------------------
//  IMAGEZOOMRENDERER
// --------------------------------------------------------------------------------

type ImageZoomRenderer struct {
	iz *ImageZoom
}

// compliant with WidgetRenderer interface (https://pkg.go.dev/fyne.io/fyne/v2#WidgetRenderer)
var _ fyne.WidgetRenderer = &ImageZoomRenderer{}

func (izr *ImageZoomRenderer) Destroy() {
}

func (izr *ImageZoomRenderer) Layout(size fyne.Size) {
	// layout func places all the widget Objects()
	// objects[0].Resize(size)
	// objects[0].Move(pos)
	// e.g. in ./fynesample/sample/sample.go wideSliderWithLabel

	cs := izr.iz.getCurrentScale()
	fmt.Printf("[%-5s] Layout: size %+v\tscale %+v\n", izr.iz.name, size, cs)

	// put the background everywhere in the widget
	izr.iz.background.Resize(size)

	imgSize := fyne.NewSize(100, 100)
	izr.iz.imgCanvas.Resize(imgSize)
	pos := fyne.NewPos(0, 0)
	izr.iz.imgCanvas.Move(pos)
}

func (izr *ImageZoomRenderer) MinSize() fyne.Size {
	return izr.iz.minSize
}

func (izr *ImageZoomRenderer) Objects() []fyne.CanvasObject {
	return []fyne.CanvasObject{izr.iz.background, izr.iz.imgCanvas}
}

func (izr *ImageZoomRenderer) Refresh() {
	canvas.Refresh(izr.iz)
}

// --------------------------------------------------------------------------------
//  IMAGEZOOM
// --------------------------------------------------------------------------------

type ImageZoom struct {
	widget.BaseWidget

	a    *myApp
	name string

	minSize fyne.Size

	background   *canvas.Raster
	backCellSize int

	imgOrig   *image.RGBA
	imgCanvas *canvas.Image
}

func newImageZoom(a *myApp, name string) *ImageZoom {
	iz := &ImageZoom{a: a, name: name}

	iz.minSize = fyne.NewSize(400, 400)

	iz.background = canvas.NewRasterWithPixels(iz.bgPattern)
	iz.backCellSize = 50

	pixW := 200
	pixH := 200
	img := image.NewRGBA(image.Rect(0, 0, pixW, pixH))
	draw.Draw(
		img, img.Bounds(),
		&image.Uniform{color.RGBA{10, 10, 10, 255}},
		image.Point{0, 0},
		draw.Src)
	iz.imgOrig = img
	iz.imgCanvas = canvas.NewImageFromImage(iz.imgOrig)

	// imgURI := storage.NewFileURI("https://via.placeholder.com/750x150.png")
	// iz.imgCanvas = canvas.NewImageFromURI(imgURI)
	// if img, ok := iz.imgCanvas.Image.(*image.RGBA); ok {
	// 	iz.imgOrig = img
	// }

	iz.ExtendBaseWidget(iz)
	return iz
}

// compliant with Widget interface (https://pkg.go.dev/fyne.io/fyne/v2#Widget)
var _ fyne.Widget = &ImageZoom{}

func (iz *ImageZoom) CreateRenderer() fyne.WidgetRenderer {
	return &ImageZoomRenderer{iz: iz}
}

// compliant with Mouseable interface (https://pkg.go.dev/fyne.io/fyne/v2/driver/desktop#Mouseable)
var _ desktop.Mouseable = &ImageZoom{}

func (iz *ImageZoom) MouseDown(ev *desktop.MouseEvent) {
	fmt.Printf("[%-5s] MouseDown ev = %+v\n", iz.name, ev)
}

func (iz *ImageZoom) MouseUp(ev *desktop.MouseEvent) {
	fmt.Printf("[%-5s] MouseUp   ev = %+v\n", iz.name, ev)
}

// compliant with Hoverable interface (https://pkg.go.dev/fyne.io/fyne/v2/driver/desktop#Hoverable)
var _ desktop.Hoverable = &ImageZoom{}

func (iz *ImageZoom) MouseIn(ev *desktop.MouseEvent) {
	fmt.Printf("MouseIn ev = %+v\n", ev)
}

func (iz *ImageZoom) MouseMoved(ev *desktop.MouseEvent) {
	// fmt.Printf("MouseMoved ev = %+v\n", ev)
}

func (iz *ImageZoom) MouseOut() {
	fmt.Print("MouseOut\n")
}

// compliant with Scrollable interface (https://pkg.go.dev/fyne.io/fyne/v2#Scrollable)
var _ fyne.Scrollable = &ImageZoom{}

func (iz *ImageZoom) Scrolled(ev *fyne.ScrollEvent) {
	fmt.Printf("Scrolled ev = %+v\n", ev)
}

// ----- MISC -----

func (iz *ImageZoom) bgPattern(x, y, _, _ int) color.Color {
	if (x/iz.backCellSize)%2 == (y/iz.backCellSize)%2 {
		return color.Gray{Y: 50}
	}
	return color.Gray{Y: 80}
}

func (iz *ImageZoom) getCurrentScale() float32 {
	// get the current scale of the main window
	return iz.a.mainWin.Canvas().Scale()
}

// --------------------------------------------------------------------------------
//  APPLICATION
// --------------------------------------------------------------------------------

type myApp struct {
	fyneApp fyne.App
	mainWin fyne.Window

	imageZoom *ImageZoom

	label1 *widget.Label
	label2 *widget.Label

	input   *widget.Entry
	saveBtn *widget.Button
}

func newApp() *myApp {

	// create the app
	fyneApp := app.New()
	mainWin := fyneApp.NewWindow("Image test")
	theApp := &myApp{fyneApp: fyneApp, mainWin: mainWin}

	// add the link for typed runes
	theApp.mainWin.Canvas().SetOnTypedKey(theApp.typedKey)

	return theApp
}

func (a *myApp) buildUI() {

	a.imageZoom = newImageZoom(a, "img")
	contentImg := a.imageZoom

	a.label1 = widget.NewLabel("Hello there")
	a.label2 = widget.NewLabel("(right aligned)")
	contentTitle := container.New(layout.NewHBoxLayout(), a.label1, layout.NewSpacer(), a.label2)

	a.input = widget.NewEntry()
	a.input.SetPlaceHolder("Enter text...")
	a.input.OnSubmitted = a.inputSubmitted
	a.saveBtn = widget.NewButton("Save", a.btnPressSave)
	contentInput := container.New(layout.NewBorderLayout(nil, nil, nil, a.saveBtn),
		a.saveBtn, a.input)

	borderCont := container.New(layout.NewBorderLayout(contentTitle, contentInput, nil, nil),
		contentTitle, contentInput, contentImg)

	a.mainWin.SetContent(borderCont)
}

func (a *myApp) btnPressSave() {
	fmt.Println("Content was:", a.input.Text)
}

func (a *myApp) inputSubmitted(s string) {
	fmt.Printf("Content was: %q received %q\n", a.input.Text, s)
}

func (a *myApp) typedKey(ev *fyne.KeyEvent) {
	fmt.Printf("typedKey  = %+v %T\n", ev, ev)
	switch ev.Name {
	case fyne.KeyEscape, fyne.KeyQ:
		a.fyneApp.Quit()
	default:
	}
}

func (a *myApp) runApp() {
	a.mainWin.Resize(fyne.NewSize(1200, 1200))
	a.mainWin.Show()
	a.fyneApp.Run()
}

// --------------------------------------------------------------------------------
//  MAIN
// --------------------------------------------------------------------------------

func main() {
	fmt.Println("vim-go")

	// create the app
	theApp := newApp()

	// build the UI
	theApp.buildUI()

	// show the app
	theApp.runApp()
}
