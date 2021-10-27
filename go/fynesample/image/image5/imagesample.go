package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"math"
	"os"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/driver/desktop"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"
	xdraw "golang.org/x/image/draw"
)

// ##### UTILS #####

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

func newSizeFloat64(w, h float64) fyne.Size {
	return fyne.NewSize(float32(w), float32(h))
}

func newPosFloat64(x, y float64) fyne.Position {
	return fyne.NewPos(float32(x), float32(y))
}

func newRectangleFloat64(left, top, right, bottom float64) image.Rectangle {
	// we need the int closest to the float64
	// 800.000000 sometimes was converted to 799
	return image.Rectangle{
		Min: image.Point{int(left + 0.5), int(top + 0.5)},
		Max: image.Point{int(right + 0.5), int(bottom + 0.5)},
	}
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
	iz.wWid = float64(iz.currSize.Width)
	iz.hWid = float64(iz.currSize.Height)

	// reset the image and redraw everything
	iz.resetImageZoom()

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
	// iz.imgCanvas.Move(fyne.NewPos(0, 0))
	canvas.Refresh(iz)
}

// --------------------------------------------------------------------------------
//  IMAGEZOOM
// --------------------------------------------------------------------------------

type ImageZoom struct {
	widget.BaseWidget

	a    *myApp // the main app
	name string // name of the widget

	minSize fyne.Size // minimum size of the widget

	background   *canvas.Raster // raster for the background
	backCellSize int            // size of the background cells

	imgOrig *image.RGBA // original image
	wOri    float64     // original image width
	hOri    float64     // original image height

	imgCanvas *canvas.Image // canvas to draw the image on
	xCan      float64       // x position of the canvas in the widget
	yCan      float64       // y position of the canvas in the widget

	currSize fyne.Size // current size of the widget
	wWid     float64
	hWid     float64

	zoomBase  float64 // zoom saved in log scale, actual zoom: zoomBase**zoomLevel
	zoomBaseI float64 // precomputed to save time: log_b(x)=log(x)/log(b)
	zoomLevel float64 // current zoom level in log scale

	xMov float64 // position of the left corner to show
	yMov float64 // position of the top corner to show

	xMouse float64 // x position of the mouse
	yMouse float64 // y position of the mouse
}

func newImageZoom(a *myApp, name string, filePath string) *ImageZoom {
	iz := &ImageZoom{a: a, name: name}

	iz.minSize = fyne.NewSize(400, 600)
	iz.zoomBase = math.Sqrt(2)
	iz.zoomBaseI = 1 / math.Log(iz.zoomBase)

	iz.background = canvas.NewRasterWithPixels(iz.bgPattern)
	iz.backCellSize = 50

	iz.imgOrig, _, _ = getRGBAFromFilePath(filePath)
	imgOriSize := iz.imgOrig.Rect.Size()
	iz.wOri = float64(imgOriSize.X)
	iz.hOri = float64(imgOriSize.Y)

	iz.imgCanvas = canvas.NewImageFromImage(iz.imgOrig)
	iz.imgCanvas.ScaleMode = canvas.ImageScalePixels
	// iz.imgCanvas.FillMode = canvas.ImageFillStretch
	iz.imgCanvas.FillMode = canvas.ImageFillContain

	iz.ExtendBaseWidget(iz)
	return iz
}

// ##### INTERFACES IZ #####

// compliant with Widget interface (https://pkg.go.dev/fyne.io/fyne/v2#Widget)
var _ fyne.Widget = &ImageZoom{}

func (iz *ImageZoom) CreateRenderer() fyne.WidgetRenderer {
	return &ImageZoomRenderer{iz: iz}
}

// compliant with Mouseable interface (https://pkg.go.dev/fyne.io/fyne/v2/driver/desktop#Mouseable)
var _ desktop.Mouseable = &ImageZoom{}

func (iz *ImageZoom) MouseDown(ev *desktop.MouseEvent) {
	fmt.Printf("[%-4s] MouseDown  ev = %+v\n", iz.name, ev)
	switch ev.Button {
	case desktop.MouseButtonPrimary:
		// iz.Refresh()
		iz.xMouse = float64(ev.PointEvent.Position.X)
		iz.yMouse = float64(ev.PointEvent.Position.Y)
	case desktop.MouseButtonSecondary:
		// iz.artisanalRefresh()
	}
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
	fmt.Printf("[%-4s] MouseMoved ev = %+v\n", iz.name, ev)
	switch ev.Button {
	case desktop.MouseButtonPrimary:
		xMouseOld, yMouseOld := iz.xMouse, iz.yMouse
		iz.xMouse = float64(ev.PointEvent.Position.X)
		iz.yMouse = float64(ev.PointEvent.Position.Y)
		iz.moveImage(xMouseOld-iz.xMouse, yMouseOld-iz.yMouse)
	}
}

func (iz *ImageZoom) MouseOut() {
	fmt.Printf("[%-4s] MouseOut\n", iz.name)
}

// compliant with Scrollable interface (https://pkg.go.dev/fyne.io/fyne/v2#Scrollable)
var _ fyne.Scrollable = &ImageZoom{}

func (iz *ImageZoom) Scrolled(ev *fyne.ScrollEvent) {
	fmt.Printf("[%-4s] Scrolled   ev = %+v\n", iz.name, ev)
	x := float64(ev.Position.X)
	y := float64(ev.Position.Y)
	var direction string
	if ev.Scrolled.DY > 0 {
		direction = "in"
	} else {
		direction = "out"
	}
	iz.changeZoom(direction, x, y)
}

// ##### MISC IZ #####

func (iz *ImageZoom) bgPattern(x, y, _, _ int) color.Color {
	if (x/iz.backCellSize)%2 == (y/iz.backCellSize)%2 {
		return color.Gray{Y: 50}
	}
	return color.Gray{Y: 80}
}

// ##### IMPLEMENTATION IZ #####

// Set the zoomLevel so that the image fits exactly the currSize
func (iz *ImageZoom) resetImageZoom() {
	// MAYBE we need to check that the value is good

	if iz.wOri < iz.wWid && iz.hOri < iz.hWid {
		iz.zoomLevel = 0
	} else {
		ratio := math.Min(iz.wWid/iz.wOri, iz.hWid/iz.hOri)
		iz.zoomLevel = math.Log(ratio) * iz.zoomBaseI
	}
	fmt.Printf("[%-4s] resetImageZoom %+v\n", iz.name, iz.zoomLevel)

	iz.xMov = 0
	iz.yMov = 0

	iz.redrawImageZoom()
}

// Update the src region, resize and move the dst canvas
func (iz *ImageZoom) redrawImageZoom() {
	fmt.Printf("[%-4s] redrawImageZoom\n", iz.name)

	// current zoom in linear scale
	zoom := math.Pow(iz.zoomBase, iz.zoomLevel)

	// size of the virtual zoomed image
	wZum := math.Ceil(float64(iz.wOri * zoom))
	hZum := math.Ceil(float64(iz.hOri * zoom))
	fmt.Printf("       virtual img = %+vx%+v zoom %+v\n",
		wZum, hZum, zoom)

	wWid, hWid := iz.wWid, iz.hWid // current widget size
	wOri, hOri := iz.wOri, iz.hOri // original image size
	xMov, yMov := iz.xMov, iz.yMov // position

	// SubImage returns an image representing
	// the portion of the image visible through the region
	// Rectangle contains the points with Min.X<=X<Max.X, Min.Y<=Y<Max.Y
	// iz.imgOrig.SubImage(region)

	var wRes, hRes float64               // the final dimension of the image to show
	var left, top, right, bottom float64 // sides of the src region to show

	// the zoomed photo fits inside the widget
	if wZum <= wWid && hZum <= hWid {
		// resize the pic, don't cut it
		wRes, hRes = wZum, hZum
		// take the entire image
		left = 0
		top = 0
		right = wOri
		bottom = hOri
	} else
	// the zoomed photo is wider than the widget
	if wZum > wWid && hZum <= hWid {
		// resized dimension as wide as the widget
		wRes, hRes = wWid, hZum
		// from top to bottom, only show a vertical stripe of the image
		left = xMov / zoom
		top = 0
		right = (xMov + wWid) / zoom
		bottom = hOri
	} else
	// the zoomed photo is taller than the widget
	if wZum <= wWid && hZum > hWid {
		// resized dimension as tall as the widget
		wRes, hRes = wZum, hWid
		// from left to right, only show an horizontal stripe of the image
		left = 0
		top = yMov / zoom
		right = wOri
		bottom = (yMov + hWid) / zoom
	} else
	// the zoomed photo is bigger than the widget
	if wZum > wWid && hZum > hWid {
		wRes, hRes = wWid, hWid
		left = xMov / zoom
		top = yMov / zoom
		right = (xMov + wWid) / zoom
		bottom = (yMov + hWid) / zoom
	}

	// validate the region: risk of a distorted image, better be safe
	if left < 0 {
		left = 0
	}
	if top < 0 {
		top = 0
	}
	if right > wOri {
		right = wOri
	}
	if bottom > hOri {
		bottom = hOri
	}

	// pack the data in the appropriate types
	wRegion := right - left
	hRegion := bottom - top
	fmt.Printf("       resSize %.3fx%.3f region (%.3f,%.3f)x(%.3f,%.3f):%.3fx%.3f ratio res %.3f reg %.3f\n",
		wRes, hRes,
		left, top, right, bottom,
		wRegion, hRegion,
		wRes/hRes, wRegion/hRegion,
	)
	resSize := newSizeFloat64(wRes, hRes)
	region := newRectangleFloat64(left, top, right, bottom)
	fmt.Printf("       resSize %+v region %+v %dx%d\n",
		resSize, region,
		region.Max.X-region.Min.X,
		region.Max.Y-region.Min.Y,
	)

	// extract the subImage and set it in the canvas
	// subImage := iz.imgOrig.SubImage(region)
	subImage := image.NewRGBA(newRectangleFloat64(0, 0, wRes, hRes))
	// draw.Draw(subImage, subImage.Bounds(),
	// 	&image.Uniform{color.RGBA{10, 10, 10, 255}},
	// 	image.Point{0, 0}, draw.Src)
	// draw.Draw(subImage, region, iz.imgOrig, image.Pt(int(iz.xMov), int(iz.yMov)), draw.Src)
	// https://stackoverflow.com/a/67678654/2237151
	xdraw.NearestNeighbor.Scale(subImage, subImage.Rect,
		iz.imgOrig, region, draw.Over, nil)
	iz.imgCanvas.Image = subImage

	// resize and place the canvas
	iz.imgCanvas.Resize(resSize)
	iz.xCan = (wWid - wRes) / 2
	iz.yCan = (hWid - hRes) / 2
	pos := newPosFloat64(iz.xCan, iz.yCan)
	iz.imgCanvas.Move(pos)

	canvas.Refresh(iz.imgCanvas)

}

// Change zoom level, keeping (x, y) still
func (iz *ImageZoom) changeZoom(direction string, xPos, yPos float64) {
	fmt.Printf("[%-4s] changeZoom %s\n", iz.name, direction)

	// pos in in the widget
	// we want rel from the corner of the canvas
	xRel := xPos - iz.xCan
	yRel := yPos - iz.yCan

	xMov, yMov := iz.xMov, iz.yMov // position

	// old zoom in linear scale
	zoomOld := math.Pow(iz.zoomBase, iz.zoomLevel)
	wZumOld := math.Ceil(float64(iz.wOri * zoomOld))
	hZumOld := math.Ceil(float64(iz.hOri * zoomOld))
	fmt.Printf("       OLD virtual img = %+vx%+v zoom %.3f mov %.3fx%.3f rel %.3fx%.3f\n",
		wZumOld, hZumOld,
		zoomOld,
		xMov, yMov,
		xRel, yRel,
	)

	switch direction {
	case "in":
		iz.zoomLevel += 1
	case "out":
		iz.zoomLevel -= 1
	case "reset":
		iz.resetImageZoom()
		return
	}

	// new zoom in linear scale
	zoomNew := math.Pow(iz.zoomBase, iz.zoomLevel)
	wZumNew := math.Ceil(float64(iz.wOri * zoomNew))
	hZumNew := math.Ceil(float64(iz.hOri * zoomNew))

	// if we can generate zoom events without a set (x, y) position
	// we have to compute the center of the canvas

	xMovNew := (xMov+xRel)*zoomNew/zoomOld - xRel
	yMovNew := (yMov+yRel)*zoomNew/zoomOld - yRel

	// validate the new mov computed
	// check that it does not try to go outside the image

	// if xMovNew < 0 {
	// 	xMovNew = 0
	// }
	// if yMovNew < 0 {
	// 	yMovNew = 0
	// }
	// if wZumNew <= wWid && hZumNew <= hWid {
	// 	xMovNew = 0
	// 	yMovNew = 0
	// } else if wZumNew > wWid && hZumNew <= hWid {
	// 	if xMovNew+wWid > wZumNew {
	// 		xMovNew = wZumNew - wWid
	// 	}
	// 	yMovNew = 0
	// } else if wZumNew <= wWid && hZumNew > hWid {
	// 	xMovNew = 0
	// 	if yMovNew+hWid > hZumNew {
	// 		yMovNew = hZumNew - hWid
	// 	}
	// } else if wZumNew > wWid && hZumNew > hWid {
	// 	if xMovNew+wWid > wZumNew {
	// 		xMovNew = wZumNew - wWid
	// 	}
	// 	if yMovNew+hWid > hZumNew {
	// 		yMovNew = hZumNew - hWid
	// 	}
	// }

	// assign possibly bad values and validate them
	iz.xMov, iz.yMov = xMovNew, yMovNew

	iz.validateMov()

	fmt.Printf("       NEW virtual img = %+vx%+v zoom %.3f mov %.3fx%.3f\n",
		wZumNew, hZumNew, zoomNew, xMovNew, yMovNew)

	iz.redrawImageZoom()
}

// Move the position inside the virtual image
func (iz *ImageZoom) moveImage(dx, dy float64) {
	iz.xMov += dx
	iz.yMov += dy
	iz.validateMov()
	iz.redrawImageZoom()
}

// Ensure that the virtual pos has reasonable values
func (iz *ImageZoom) validateMov() {

	wWid, hWid := iz.wWid, iz.hWid // current widget size

	// new zoom in linear scale
	zoom := math.Pow(iz.zoomBase, iz.zoomLevel)
	wZum := math.Ceil(float64(iz.wOri * zoom))
	hZum := math.Ceil(float64(iz.hOri * zoom))

	// the new image is thinner than the widget
	if wZum <= wWid {
		fmt.Printf("FIXED iz.xMov a = %.3f\n", iz.xMov)
		iz.xMov = 0
	} else
	// the new image is wider than the widget
	{
		// check if the region will try to go outside the image
		if iz.xMov+wWid > wZum {
			fmt.Printf("FIXED iz.xMov b %.3f %.3f\n", iz.xMov, wZum-wWid)
			iz.xMov = wZum - wWid
		}
		if iz.xMov < 0 {
			fmt.Printf("FIXED iz.xMov c %.3f 0\n", iz.xMov)
			iz.xMov = 0
		}
	}

	// the new image is shorter than the widget
	if hZum <= hWid {
		fmt.Printf("FIXED iz.yMov a = %.3f\n", iz.yMov)
		iz.yMov = 0
	} else
	// the new image is taller than the widget
	{
		// check if the region will try to go outside the image
		if iz.yMov+hWid > hZum {
			fmt.Printf("FIXED iz.yMov b %.3f %.3f\n", iz.yMov, hZum-hWid)
			iz.yMov = hZum - hWid
		}
		if iz.yMov < 0 {
			fmt.Printf("FIXED iz.yMov c %.3f 0\n", iz.yMov)
			iz.yMov = 0
		}
	}
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
