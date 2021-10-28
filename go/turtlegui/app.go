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
)

type myApp struct {
	c *myController

	fyneApp fyne.App
	mainWin fyne.Window

	s *mySidebar

	img *canvas.Image
}

func newApp(c *myController) *myApp {

	// create the app
	fyneApp := app.New()
	mainWin := fyneApp.NewWindow("Image test")
	theApp := &myApp{fyneApp: fyneApp, mainWin: mainWin, c: c}

	// add the link for typed runes
	theApp.mainWin.Canvas().SetOnTypedKey(theApp.typedKey)

	return theApp
}

func (a *myApp) runApp() {
	a.mainWin.Resize(fyne.NewSize(1200, 1200))
	a.mainWin.Show()
	a.fyneApp.Run()
}

// --------------------------------------------------------------------------------
//  Build the app
// --------------------------------------------------------------------------------

func (a *myApp) buildUI() {

	// ##### SIDEBAR #####

	a.s = newSidebar(a)
	contSidebar := a.s.buildSidebar()

	// ##### IMAGE #####

	// just a placeholder for now
	m := image.NewRGBA(image.Rect(0, 0, 400, 400))
	draw.Draw(m, m.Bounds(), &image.Uniform{color.RGBA{10, 10, 10, 255}}, image.Point{0, 0}, draw.Src)
	a.img = canvas.NewImageFromImage(m)
	a.img.FillMode = canvas.ImageFillContain
	a.img.ScaleMode = canvas.ImageScaleFastest
	a.img.SetMinSize(fyne.NewSize(200, 200))
	allBlack := canvas.NewRectangle(color.RGBA{30, 30, 30, 255})
	imageBorder := container.NewBorder(nil, nil, nil, nil,
		allBlack, a.img)

	// ##### ASSEMBLE #####

	borderCont := container.NewBorder(nil, nil, contSidebar, nil,
		imageBorder,
	)

	a.mainWin.SetContent(borderCont)
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
//  React to change of the state model
// --------------------------------------------------------------------------------

func (a *myApp) updateImg(i *image.RGBA) {
	a.img.Image = i
	canvas.Refresh(a.img)
}
