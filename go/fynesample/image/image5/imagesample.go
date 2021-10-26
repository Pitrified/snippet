package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"os"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/driver/desktop"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"
)

// ----- MISC -----

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

func getRGBAFromFilePath(filePath string) (*image.RGBA, string, error) {
	m, format, err := getImageFromFilePath(filePath)
	if err != nil {
		return nil, "", err
	}

	// if it was a RGBA image this should be fast and work well
	if img, ok := m.(*image.RGBA); ok {
		return img, format, err
	}

	// https://stackoverflow.com/a/58259978/2237151
	b := m.Bounds()
	mRGBA := image.NewRGBA(image.Rect(0, 0, b.Dx(), b.Dy()))
	draw.Draw(mRGBA, mRGBA.Bounds(), m, b.Min, draw.Src)
	return mRGBA, format, err

}

func absFloat32(f float32) float32 {
	if f >= 0 {
		return f
	}
	return -f
}

func isSizeEqual(s1, s2 fyne.Size) bool {
	delta := s1.Subtract(s2)
	e := float32(1e-6)
	if absFloat32(delta.Height) < e && absFloat32(delta.Width) < e {
		return true
	}
	return false
}

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
	// Layout is a hook that is called if the widget needs to be laid out.
	// This should never call Refresh.
	// layout func places all the widget Objects()
	// objects[0].Resize(size) objects[0].Move(pos)
	// e.g. in ./fynesample/sample/sample.go wideSliderWithLabel
	iz := izr.iz

	// put the background everywhere in the widget
	// we only need to do this when the size of the widget changes
	iz.background.Resize(size)

	// update the current widget size
	iz.currSize = size

	// draw the new image
	izr.drawImageZoom()

	// the Refresh is automagically done, not explicitly
}

func (izr *ImageZoomRenderer) MinSize() fyne.Size {
	return izr.iz.minSize
}

func (izr *ImageZoomRenderer) Objects() []fyne.CanvasObject {
	return []fyne.CanvasObject{izr.iz.background, izr.iz.imgCanvas}
}

func (izr *ImageZoomRenderer) Refresh() {
	// Refresh is a hook that is called if the widget has updated and needs to be redrawn.
	// This might trigger a Layout.
	iz := izr.iz
	fmt.Printf("[%-4s] Refresh\n", iz.name)
	// just to test that the thing moves
	iz.imgCanvas.Move(fyne.NewPos(0, 0))
	canvas.Refresh(iz)
}

// --------------------------------------------------------------------------------

func (izr *ImageZoomRenderer) drawImageZoom() {
	iz := izr.iz
	fmt.Printf("[%-4s] drawImageZoom\n", iz.name)

	// check if the size of the widget changed
	// do we really need to check? if the draw is due to a zoom we need to
	// redraw everything anyway (not with the move tho, just change the pic)
	if !isSizeEqual(iz.currSize, iz.oldSize) {
		iz.oldSize = iz.currSize
		// compute the new zoomBase
		// MAYBE set the zoom to the base?
		// it's not the size change that triggers the redraw
		// it's the zoom change
	}

	// if !floatEqual(zoom, zoomOld) {
	// compute the size/pos for the new zoom level
	// compute the region for the new zoom level, keeping the mouse point fixed
	// }

	// check if the image moved (no zoom change), and update the source region

	// current size of the widget
	wWid := iz.currSize.Width
	hWid := iz.currSize.Height
	fmt.Printf("[%-4s] widgetSize = %+vx%+v\n", iz.name, wWid, hWid)

	// size of the original image
	imgOriSize := iz.imgOrig.Rect.Size()
	wOri := float32(imgOriSize.X)
	hOri := float32(imgOriSize.Y)

	// iz.imgOrig.SubImage(region)

	var imgSize fyne.Size
	var pos fyne.Position

	// image smaller than widget
	if wOri <= wWid && hOri <= hWid {
		imgSize = fyne.NewSize(wOri, hOri)
		pos = fyne.NewPos((wWid-wOri)/2, (hWid-hOri)/2)
	} else
	// image wider than widget
	// wOri : wWid = hOri : hSca
	if wOri > wWid && hOri <= hWid {
		hSca := hOri * wWid / wOri
		imgSize = fyne.NewSize(wWid, hSca)
		pos = fyne.NewPos(0, (hWid-hSca)/2)
	} else
	// image taller than widget
	if wOri <= wWid && hOri > hWid {
		wSca := wOri * hWid / hOri
		imgSize = fyne.NewSize(wSca, hWid)
		pos = fyne.NewPos((wWid-wSca)/2, 0)
	} else
	// image larger than widget
	{
		rw := wOri / wWid
		rh := hOri / hWid
		if rw > rh {
			// touch the sides left to right
			hSca := hOri * wWid / wOri
			imgSize = fyne.NewSize(wWid, hSca)
			pos = fyne.NewPos(0, (hWid-hSca)/2)
		} else {
			// touch the sides top to bottom
			wSca := wOri * hWid / hOri
			imgSize = fyne.NewSize(wSca, hWid)
			pos = fyne.NewPos((wWid-wSca)/2, 0)
		}
	}

	// fmt.Printf("iz.imgCanvas = %+v\n", iz.imgCanvas)
	iz.imgCanvas.Resize(imgSize)
	iz.imgCanvas.Move(pos)

	// canvas.Refresh(iz)
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

	currSize fyne.Size
	oldSize  fyne.Size
}

func newImageZoom(a *myApp, name string, filePath string) *ImageZoom {
	iz := &ImageZoom{a: a, name: name}

	iz.minSize = fyne.NewSize(400, 400)

	iz.background = canvas.NewRasterWithPixels(iz.bgPattern)
	iz.backCellSize = 50

	iz.imgOrig, _, _ = getRGBAFromFilePath(filePath)
	iz.imgCanvas = canvas.NewImageFromImage(iz.imgOrig)
	iz.imgCanvas.ScaleMode = canvas.ImageScalePixels
	iz.imgCanvas.FillMode = canvas.ImageFillContain

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
	fmt.Printf("[%-4s] MouseDown  ev = %+v\n", iz.name, ev)
	iz.Refresh()
}

func (iz *ImageZoom) MouseUp(ev *desktop.MouseEvent) {
	fmt.Printf("[%-4s] MouseUp    ev = %+v\n", iz.name, ev)
}

// compliant with Hoverable interface (https://pkg.go.dev/fyne.io/fyne/v2/driver/desktop#Hoverable)
var _ desktop.Hoverable = &ImageZoom{}

func (iz *ImageZoom) MouseIn(ev *desktop.MouseEvent) {
	fmt.Printf("[%-4s] MouseIn    ev = %+v\n", iz.name, ev)
}

func (iz *ImageZoom) MouseMoved(ev *desktop.MouseEvent) {
	// fmt.Printf("[%-4s] MouseMoved ev = %+v\n", iz.name, ev)
}

func (iz *ImageZoom) MouseOut() {
	fmt.Printf("[%-4s] MouseOut\n", iz.name)
}

// compliant with Scrollable interface (https://pkg.go.dev/fyne.io/fyne/v2#Scrollable)
var _ fyne.Scrollable = &ImageZoom{}

func (iz *ImageZoom) Scrolled(ev *fyne.ScrollEvent) {
	fmt.Printf("[%-4s] Scrolled   ev = %+v\n", iz.name, ev)
}

// ----- MISC IZ -----

func (iz *ImageZoom) bgPattern(x, y, _, _ int) color.Color {
	if (x/iz.backCellSize)%2 == (y/iz.backCellSize)%2 {
		return color.Gray{Y: 50}
	}
	return color.Gray{Y: 80}
}

// --------------------------------------------------------------------------------
//  APPLICATION
// --------------------------------------------------------------------------------

type myApp struct {
	fyneApp fyne.App
	mainWin fyne.Window

	imageZoomMain *ImageZoom
	imageZoomEcho *ImageZoom

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

	aFilePath := "../800800.png"
	// aFilePath := "../200800.png"
	// aFilePath := "../800200.png"
	// aFilePath := "../200200.png"
	a.imageZoomMain = newImageZoom(a, "main", aFilePath)
	bFilePath := "../800800.png"
	// bFilePath := "../200800.png"
	// bFilePath := "../800200.png"
	// bFilePath := "../200200.png"
	a.imageZoomEcho = newImageZoom(a, "echo", bFilePath)
	contentImg := container.New(layout.NewGridLayout(2), a.imageZoomMain, a.imageZoomEcho)

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
