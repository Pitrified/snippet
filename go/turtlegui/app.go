package main

import (
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
	fyneApp := app.NewWithID("com.pitrified.turtlegui")
	mainWin := fyneApp.NewWindow("Turtle GUI")
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
	// fmt.Printf("typedKey  = %+v %T\n", ev, ev)
	switch ev.Name {
	case fyne.KeyEscape:
		a.fyneApp.Quit()
	case fyne.KeyW, fyne.KeyS, fyne.KeyD, fyne.KeyE, fyne.KeyA, fyne.KeyQ:
		a.control(ev.Name)
	case fyne.KeySpace:
		a.c.togglePenState()
	case fyne.KeyH:
		a.s.miscHelpCB()
	default:
	}
}

func (a *myApp) control(k fyne.KeyName) {
	// extract the data from the custom pos/ori change entries
	d, errD := entry2F64(a.s.moveCustEnt)
	r, errR := entry2F64(a.s.rotCustEnt)
	if errD != nil || errR != nil {
		return
	}

	// move around by the specified amount
	switch k {
	case fyne.KeyW:
		a.c.move(d)
	case fyne.KeyS:
		a.c.move(-d)
	case fyne.KeyD:
		a.c.rotate(-r)
	case fyne.KeyE:
		a.c.move(d)
		a.c.rotate(-r)
	case fyne.KeyA:
		a.c.rotate(r)
	case fyne.KeyQ:
		a.c.move(d)
		a.c.rotate(r)
	}
}

// --------------------------------------------------------------------------------
//  React to change of the state model
// --------------------------------------------------------------------------------

func (a *myApp) updateImg(i *image.RGBA) {
	a.img.Image = i
	canvas.Refresh(a.img)
}
