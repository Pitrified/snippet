// A model/view/controller example app.
// The model does not use observables.
// The controller knows which elements must be updated after each user input.
// The view only talks with the controller.
package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"math"
	"strconv"
	"strings"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"
)

// --------------------------------------------------------------------------------
//  MISC
// --------------------------------------------------------------------------------

// Extract the float64 from an entry.
func entry2F64(e *widget.Entry) (float64, error) {
	// string in the entry
	str := e.Text
	// convert it to float
	x, err := strconv.ParseFloat(str, 64)
	if err != nil {
		fmt.Printf("Failed to parse str = %q\n", str)
		return 0, err
	}
	return x, nil
}

// Prettier format for floats, remove trailing zeros.
// https://stackoverflow.com/q/31289409/2237151
func FormatFloat(num float64, prc int) string {
	str := fmt.Sprintf("%."+strconv.Itoa(prc)+"f", num)
	return strings.TrimRight(strings.TrimRight(str, "0"), ".")
}

// --------------------------------------------------------------------------------
//  MINITURTLE
// --------------------------------------------------------------------------------

// A minimal turtle. Cannot turn.
type miniTurtle struct {
	x, y float64
	ori  float64
}

// Create a new turtle.
func newMiniTurtle() *miniTurtle {
	return &miniTurtle{ori: math.Pi / 3}
}

// Move the turtle of the specified distance.
func (t *miniTurtle) move(d float64) {
	t.x += d * math.Cos(t.ori)
	t.y += d * math.Sin(t.ori)
}

// Move the turtle of the specified distance.
func (t *miniTurtle) jump(x, y float64) {
	t.x = x
	t.y = y
}

// --------------------------------------------------------------------------------
//  CONTROLLER (no observables)
// --------------------------------------------------------------------------------

type myController struct {
	a  *myApp
	mt *miniTurtle
}

// Create a new controller, linked to the view and the model
func newController() *myController {
	c := &myController{}

	// create the view
	c.a = newApp(c)

	// create the turtle to control
	c.mt = newMiniTurtle()

	return c
}

// Create the UI and run the app.
func (c *myController) run() {

	// create the UI, using placeholders everywhere
	c.a.buildUI()

	// update all the moving parts to match the current state
	c.initAll()

	// run the app (will block)
	c.a.runApp()
}

// Update all the view elements.
func (c *myController) initAll() {
	c.updatedPos()
}

// The user requested a movement.
func (c *myController) move(d string) {

	// react to the user input and change the model state
	switch d {
	case "forward":
		c.mt.move(10)
	case "backward":
		c.mt.move(-10)
	}

	// we are NOT using observables: manually update the elements we need
	// we extract the required data and send it to the view
	// the view has no idea of where this data comes from
	c.updatedPos()
}

// The user requested a jump.
func (c *myController) jump(x, y float64) {
	c.mt.jump(x, y)
	c.updatedPos()
}

// The position has been updated in the model: update the view accordingly.
// If we had an observable, this would be the callback linked.
func (c *myController) updatedPos() {
	c.a.s.updatePos(c.mt.x, c.mt.y)
}

// --------------------------------------------------------------------------------
//  SIDEBAR
// --------------------------------------------------------------------------------

type mySidebar struct {
	a *myApp

	title *widget.Label

	moveCard     *widget.Card
	moveForward  *widget.Button
	moveBackward *widget.Button

	currLabel *widget.Label

	moveSetBtn *widget.Button
	moveSetX   *widget.Entry
	moveSetY   *widget.Entry
}

func newSidebar(a *myApp) *mySidebar {
	return &mySidebar{a: a}
}

// Update all the widget related to the pos.
func (s *mySidebar) updatePos(x, y float64) {
	// in the label, show short number if it grows
	s.currLabel.SetText(fmt.Sprintf("Current pos: (%.5g, %.5g)", x, y))
	// in the entries, always show all
	s.moveSetX.SetText(FormatFloat(x, 3))
	s.moveSetY.SetText(FormatFloat(y, 3))
}

// Clicked button move forward.
func (s *mySidebar) moveForwardCB() {
	s.a.c.move("forward")
}

// Clicked button move backward.
func (s *mySidebar) moveBackwardCB() {
	s.a.c.move("backward")
}

// Clicked button set position from entries.
func (s *mySidebar) moveSetBtnCB() {
	// if the reading fails we could check the error :D
	x, _ := entry2F64(s.moveSetX)
	y, _ := entry2F64(s.moveSetY)

	// tell the controller that we want to teleport there
	s.a.c.jump(x, y)
}

// Press enter on either set entry.
func (s *mySidebar) moveSetSubmitted(_ string) {
	s.moveSetBtnCB()
}

// Build the move card.
func (s *mySidebar) buildMove() {
	// buttons to control the movement
	s.moveForward = widget.NewButton("Forward", s.moveForwardCB)
	s.moveBackward = widget.NewButton("Backward", s.moveBackwardCB)
	contBank := container.NewGridWithColumns(2, s.moveBackward, s.moveForward)

	// label with the current position
	s.currLabel = widget.NewLabel("Current pos:")

	// ##### entries + button to set position #####

	s.moveSetBtn = widget.NewButton("Set", s.moveSetBtnCB)
	// Entry x
	s.moveSetX = widget.NewEntry()
	s.moveSetX.Text = "0.000"
	s.moveSetX.Wrapping = fyne.TextWrapOff
	s.moveSetX.OnSubmitted = s.moveSetSubmitted
	// Entry y
	s.moveSetY = widget.NewEntry()
	s.moveSetY.Text = "0.000"
	s.moveSetY.Wrapping = fyne.TextWrapOff
	s.moveSetY.OnSubmitted = s.moveSetSubmitted
	// Labels
	labMoveX := widget.NewLabel("X:")
	labMoveY := widget.NewLabel("Y:")
	// Pair label and entry
	elMoveX := container.NewBorder(nil, nil, labMoveX, nil, s.moveSetX)
	elMoveY := container.NewBorder(nil, nil, labMoveY, nil, s.moveSetY)
	// Pair the EL
	elMoveXY := container.NewGridWithColumns(2, elMoveX, elMoveY)
	// Pair the ELpair and the button
	contMoveSet := container.NewBorder(nil, nil, nil, s.moveSetBtn, elMoveXY)

	// build the card
	contCard := container.NewVBox(contBank, s.currLabel, contMoveSet)
	s.moveCard = widget.NewCard("Move", "Control the linear movement.", contCard)
}

// Build the sidebar.
func (s *mySidebar) buildSidebar() *fyne.Container {

	// A silly title
	s.title = widget.NewLabelWithStyle(
		"The title",
		fyne.TextAlignCenter,
		fyne.TextStyle{Bold: true},
	)

	s.buildMove()

	// ----- All the sidebar content -----

	vCont := container.NewVBox(s.title, s.moveCard)
	return vCont
}

// --------------------------------------------------------------------------------
//  APPLICATION
// --------------------------------------------------------------------------------

type myApp struct {
	c *myController

	fyneApp fyne.App
	mainWin fyne.Window

	s *mySidebar
}

// Create a new app.
func newApp(c *myController) *myApp {

	// create the app
	fyneApp := app.New()
	mainWin := fyneApp.NewWindow("Image test")
	theApp := &myApp{fyneApp: fyneApp, mainWin: mainWin, c: c}

	// add the link for typed runes
	theApp.mainWin.Canvas().SetOnTypedKey(theApp.typedKey)

	return theApp
}

// Create the entire UI of the app.
func (a *myApp) buildUI() {

	// ##### TOP #####

	label1 := widget.NewLabel("Hello there")
	label2 := widget.NewLabel("(right aligned)")
	contentTitle := container.NewHBox(label1, layout.NewSpacer(), label2)

	// ##### SIDEBAR #####

	a.s = newSidebar(a)
	contSidebar := a.s.buildSidebar()

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

// SetOnTypedKey callback.
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
	theController := newController()
	theController.run()
}
