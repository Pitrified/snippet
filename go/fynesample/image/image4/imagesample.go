package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/widget"
)

// --------------------------------------------------------------------------------

type myRasterRenderer struct {
	render  *canvas.Raster
	objects []fyne.CanvasObject
}

// compliant with WidgetRenderer interface
// https://pkg.go.dev/fyne.io/fyne/v2#WidgetRenderer
var _ fyne.WidgetRenderer = &myRasterRenderer{}

func (mrr *myRasterRenderer) Destroy() {
}

func (mrr *myRasterRenderer) Layout(size fyne.Size) {
	fmt.Printf("Layout = %+v\n", size)
	mrr.render.Resize(size)
}
func (mrr *myRasterRenderer) MinSize() fyne.Size {
	return fyne.NewSize(400, 400)
}

func (mrr *myRasterRenderer) Objects() []fyne.CanvasObject {
	return mrr.objects
}

func (mrr *myRasterRenderer) Refresh() {
	canvas.Refresh(mrr.render)
}

func (mr *myRasterRenderer) rasterUpdate(w, h int) image.Image {
	fmt.Printf("rasterUpdate : w, h = %+v %+v\n", w, h)
	pixW := w
	pixH := h
	img := image.NewRGBA(image.Rect(0, 0, pixW, pixH))
	draw.Draw(img, img.Bounds(), &image.Uniform{color.RGBA{10, 10, 10, 255}}, image.Point{0, 0}, draw.Src)
	return img
}

// --------------------------------------------------------------------------------

type myRaster struct {
	widget.BaseWidget
}

// compliant with Widget interface
// https://pkg.go.dev/fyne.io/fyne/v2#Widget
var _ fyne.Widget = &myRaster{}

func (mr *myRaster) CreateRenderer() fyne.WidgetRenderer {
	renderer := &myRasterRenderer{}

	render := canvas.NewRaster(renderer.rasterUpdate)
	render.ScaleMode = canvas.ImageScalePixels

	renderer.render = render
	renderer.objects = []fyne.CanvasObject{render}

	return renderer
}

func newMyRaster() *myRaster {
	mr := &myRaster{}
	mr.ExtendBaseWidget(mr)
	return mr
}

// --------------------------------------------------------------------------------

func main() {
	fmt.Println("vim-go")

	myApp := app.New()
	w := myApp.NewWindow("Image test")

	// create the photo app
	// game := newGame(board)
	// build the UI
	// window.SetContent(game.buildUI())
	// add the link for typed runes
	// window.Canvas().SetOnTypedRune(game.typedRune)
	// start the animation
	// game.animate()

	// raster := canvas.NewRaster(rasterUpdate)
	// raster.SetMinSize(fyne.NewSize(600, 600))

	// text1 := canvas.NewText("Hello", color.White)
	// text2 := canvas.NewText("There", color.RGBA{150, 75, 0, 255})
	// text3 := canvas.NewText("(right)", color.White)
	// contentTop := container.New(layout.NewHBoxLayout(), text1, text2, layout.NewSpacer(), text3)

	// input := widget.NewEntry()
	// input.SetPlaceHolder("Enter text...")
	// inp_content := container.NewVBox(input, widget.NewButton("Save", func() {
	// 	log.Println("Content was:", input.Text)
	// }))

	// borderCont := container.New(layout.NewBorderLayout(contentTop, inp_content, nil, nil),
	// 	contentTop, inp_content, raster)

	// w.SetContent(borderCont)

	aRaster := newMyRaster()

	w.SetContent(aRaster)

	w.Resize(fyne.NewSize(1200, 1200))

	w.Show()
	myApp.Run()
}
