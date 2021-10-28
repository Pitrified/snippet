package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"math"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/data/binding"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"
)

func FGet(f binding.Float) float64 {
	v, err := f.Get()
	if err != nil {
		return 0
	}
	return v
}

// --------------------------------------------------------------------------------
//  MINITURTLE
// --------------------------------------------------------------------------------

type miniTurtle struct {
	x, y binding.Float
	ori  float64

	// x, y binding.ExternalFloat
	// EF also has Reload method
	// f := 0.0
	// bf := binding.BindFloat(&f) // this also returns an ExternalFloat
}

func newMiniTurtle() *miniTurtle {
	mt := &miniTurtle{ori: math.Pi / 3}
	mt.x = binding.NewFloat()
	mt.y = binding.NewFloat()
	return mt
}

func (t *miniTurtle) move(d float64) {
	t.x.Set(FGet(t.x) + d*math.Cos(t.ori))
	t.y.Set(FGet(t.y) + d*math.Sin(t.ori))

}

// --------------------------------------------------------------------------------
//  SIDEBAR
// --------------------------------------------------------------------------------

type mySidebar struct {
	a *myApp

	title *widget.Label

	move         *widget.Card
	moveForward  *widget.Button
	moveBackward *widget.Button
}

func newSidebar(a *myApp) *mySidebar {
	return &mySidebar{a: a}
}

// Clicked button move forward
func (s *mySidebar) moveForwardCB() {
	s.a.mt.move(10)
}

// Clicked button move backward
func (s *mySidebar) moveBackwardCB() {
	s.a.mt.move(-10)
}

// Build the move card
func (s *mySidebar) buildMove() {
	// title := widget.NewLabel("Move here")

	// buttons to control the movement
	s.moveForward = widget.NewButton("10", s.moveForwardCB)
	s.moveBackward = widget.NewButton("-10", s.moveBackwardCB)
	contBank := container.NewGridWithColumns(2, s.moveBackward, s.moveForward)

	// bind a string to the float
	strX := binding.FloatToStringWithFormat(s.a.mt.x, "X: %.3f")
	currLabelX := widget.NewLabelWithData(strX)
	strY := binding.FloatToStringWithFormat(s.a.mt.y, "Y: %.3f")
	currLabelY := widget.NewLabelWithData(strY)
	contCurr := container.NewGridWithColumns(2, currLabelX, currLabelY)

	// build the card
	contCard := container.NewVBox(contBank, contCurr)
	s.move = widget.NewCard("Move", "Control the linear movement.", contCard)
}

// Build the sidebar
func (s *mySidebar) buildSidebar() *fyne.Container {

	// A silly title
	s.title = widget.NewLabelWithStyle(
		"The title",
		fyne.TextAlignCenter,
		fyne.TextStyle{Bold: true},
	)

	s.buildMove()

	// ----- All the sidebar content -----

	vCont := container.NewVBox(s.title, s.move)
	return vCont
}

// --------------------------------------------------------------------------------
//  APPLICATION
// --------------------------------------------------------------------------------

type myApp struct {
	fyneApp fyne.App
	mainWin fyne.Window

	sidebar *mySidebar

	mt *miniTurtle
}

// Create a new app
//
// Also link it directly to the model (miniTurtle)
func newApp() *myApp {

	// create the app
	fyneApp := app.New()
	mainWin := fyneApp.NewWindow("Image test")
	theApp := &myApp{fyneApp: fyneApp, mainWin: mainWin}

	// add the link for typed runes
	theApp.mainWin.Canvas().SetOnTypedKey(theApp.typedKey)

	// create the turtle to control
	theApp.mt = newMiniTurtle()

	return theApp
}

// Create the app entire UI
func (a *myApp) buildUI() {

	// ##### TOP #####

	label1 := widget.NewLabel("Hello there")
	label2 := widget.NewLabel("(right aligned)")
	contentTitle := container.NewHBox(label1, layout.NewSpacer(), label2)

	// ##### SIDEBAR #####

	a.sidebar = newSidebar(a)
	contSidebar := a.sidebar.buildSidebar()

	// ##### IMAGE #####

	img := image.NewRGBA(image.Rect(0, 0, 400, 400))
	draw.Draw(img, img.Bounds(), &image.Uniform{color.RGBA{10, 10, 10, 255}}, image.Point{0, 0}, draw.Src)

	cImg := canvas.NewImageFromImage(img)
	cImg.FillMode = canvas.ImageFillContain
	cImg.ScaleMode = canvas.ImageScaleFastest
	cImg.SetMinSize(fyne.NewSize(200, 200))

	allBlack := canvas.NewRectangle(color.RGBA{30, 30, 30, 255})
	imageBorder := container.NewBorder(nil, nil, nil, nil, allBlack, cImg)

	// ##### ASSEMBLE #####

	borderCont := container.NewBorder(contentTitle, nil, contSidebar, nil,
		imageBorder,
	)

	a.mainWin.SetContent(borderCont)
}

// SetOnTypedKey callback
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

	theApp := newApp()
	theApp.buildUI()
	theApp.runApp()
}
