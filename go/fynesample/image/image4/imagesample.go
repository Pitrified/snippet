package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/driver/desktop"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"
)

// --------------------------------------------------------------------------------

type myRasterRenderer struct {
	myRaster *myRaster
}

// compliant with WidgetRenderer interface
// https://pkg.go.dev/fyne.io/fyne/v2#WidgetRenderer
var _ fyne.WidgetRenderer = &myRasterRenderer{}

func (mrr *myRasterRenderer) Destroy() {
}

// layout func places all the widget Objects()
// in this case we just need to resize the whole raster
// objects[0].Resize(size)
// objects[0].Move(pos)
// e.g. in ./fynesample/sample/sample.go wideSliderWithLabel
func (mrr *myRasterRenderer) Layout(size fyne.Size) {
	fmt.Printf("[%-5s] Layout = %+v\n", mrr.myRaster.name, size)
	mrr.myRaster.raster.Resize(size)
}

func (mrr *myRasterRenderer) MinSize() fyne.Size {
	return mrr.myRaster.minSize
}

func (mrr *myRasterRenderer) Objects() []fyne.CanvasObject {
	return []fyne.CanvasObject{mrr.myRaster.raster}
}

func (mrr *myRasterRenderer) Refresh() {
	canvas.Refresh(mrr.myRaster)
}

// --------------------------------------------------------------------------------

type myRaster struct {
	widget.BaseWidget

	raster  *canvas.Raster
	minSize fyne.Size

	backColor uint8
	name      string
}

// compliant with Widget interface
// https://pkg.go.dev/fyne.io/fyne/v2#Widget
var _ fyne.Widget = &myRaster{}

func (mr *myRaster) CreateRenderer() fyne.WidgetRenderer {
	return &myRasterRenderer{myRaster: mr}
}

// compliant with Mouseable interface
// https://pkg.go.dev/fyne.io/fyne/v2#Widget
var _ desktop.Mouseable = &myRaster{}

func (mr *myRaster) MouseDown(ev *desktop.MouseEvent) {
	fmt.Printf("[%-5s] MouseDown ev = %+v\n", mr.name, ev)
}

func (mr *myRaster) MouseUp(ev *desktop.MouseEvent) {
	fmt.Printf("[%-5s] MouseUp   ev = %+v\n", mr.name, ev)
}

// update the raster
func (mr *myRaster) rasterUpdate(w, h int) image.Image {
	fmt.Printf("[%-5s] rasterUpdate : w, h = %+v %+v\n", mr.name, w, h)
	pixW, pixH := w, h
	img := image.NewRGBA(image.Rect(0, 0, pixW, pixH))
	bc := mr.backColor
	draw.Draw(
		img,
		img.Bounds(),
		&image.Uniform{color.RGBA{bc, bc, bc, 255}},
		image.Point{0, 0},
		draw.Src,
	)
	// this shows the problem with scaling (FYNE_SCALE=0.5 go run .)
	// the raster is drawn pixel by pixel, disregarding the scale
	// the position of the MouseEvent is scaled
	// fmt.Printf("a.mainWin.Canvas().Scale() = %+v\n", a.mainWin.Canvas().Scale())
	draw.Draw(
		img,
		image.Rect(0, 0, 100, 100),
		&image.Uniform{color.RGBA{10, 10, 10, 255}},
		image.Point{0, 0},
		draw.Src,
	)
	return img
}

// create a new raster
func newMyRaster(bc uint8, name string) *myRaster {
	mr := &myRaster{backColor: bc, name: name}

	raster := canvas.NewRaster(mr.rasterUpdate)
	raster.ScaleMode = canvas.ImageScalePixels
	mr.raster = raster

	mr.minSize = fyne.NewSize(400, 400)

	mr.ExtendBaseWidget(mr)
	return mr
}

// --------------------------------------------------------------------------------

type myApp struct {
	fyneApp fyne.App
	mainWin fyne.Window

	aRaster *myRaster
	bRaster *myRaster

	label1 *widget.Label
	label2 *widget.Label

	input   *widget.Entry
	saveBtn *widget.Button
}

func (a *myApp) btnPressSave() {
	fmt.Println("Content was:", a.input.Text)
}

func (a *myApp) inputSubmitted(s string) {
	fmt.Printf("Content was: %q received %q\n", a.input.Text, s)
}

func (a *myApp) buildUI() fyne.CanvasObject {

	a.aRaster = newMyRaster(140, "Left")
	a.bRaster = newMyRaster(40, "Right")
	doubleRaster := container.New(layout.NewGridLayout(2), a.aRaster, a.bRaster)

	// colors might be cool but should be set with the theme
	// a.text1 = canvas.NewText("Hello", color.White)
	// a.text2 = canvas.NewText("There", color.RGBA{150, 75, 0, 255})
	// a.text3 = canvas.NewText("(right aligned)", color.White)
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
		contentTitle, contentInput, doubleRaster)

	return borderCont
}

// animate controls the drawing of the current state
func (a *myApp) animate() {
	go func() {
		// Refresh rate limiter
		tickRefresh := time.NewTicker(time.Second * 2)

		// Simulation rate limiter
		tickSimulate := time.NewTicker(time.Second / 50)

		for {

			select {

			case <-tickRefresh.C:
				a.aRaster.Refresh()
				a.bRaster.Refresh()
				// here the scale is set correctly
				fmt.Printf("a.mainWin.Canvas().Scale() = %+v\n", a.mainWin.Canvas().Scale())

			case <-tickSimulate.C:
				a.aRaster.backColor += 1
				if a.aRaster.backColor > 200 {
					a.aRaster.backColor = 40
				}
				a.bRaster.backColor += 1
				if a.bRaster.backColor > 200 {
					a.bRaster.backColor = 40
				}

			}

		}
	}()
}

func (a *myApp) typedKey(ev *fyne.KeyEvent) {
	fmt.Printf("typedKey  = %+v %T\n", ev, ev)
	switch ev.Name {
	case fyne.KeyEscape, fyne.KeyQ:
		a.fyneApp.Quit()
	default:
	}
}

// --------------------------------------------------------------------------------

func main() {
	fmt.Println("vim-go")

	// create the app
	fyneApp := app.New()
	w := fyneApp.NewWindow("Image test")
	theApp := &myApp{fyneApp: fyneApp, mainWin: w}

	// always 1, need to start the mainloop before the value is set
	fmt.Printf("w.Canvas().Scale() = %+v\n", w.Canvas().Scale())

	// build the UI
	w.SetContent(theApp.buildUI())

	// add the link for typed runes
	// TODO move it a theApp := createNewApp() func?
	w.Canvas().SetOnTypedKey(theApp.typedKey)

	// start the animation
	theApp.animate()

	// show the app
	w.Resize(fyne.NewSize(1200, 1200))
	w.Show()
	fyneApp.Run()
}
