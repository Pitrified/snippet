package main

import (
	"image/color"
	"math"

	"github.com/Pitrified/go-turtle"
	"github.com/Pitrified/go-turtle/fractal"
)

type myController struct {
	a *myApp
	t *turtle.TurtleDraw
	w *turtle.World
}

// Create a new controller, linked to the view and the model
func newController() *myController {
	c := &myController{}

	// create the view
	c.a = newApp(c)

	// create a new world to draw in
	c.w = turtle.NewWorld(3840, 2160)
	// create the turtle to control
	c.t = turtle.NewTurtleDraw(c.w)
	c.t.SetPos(3840/2, 2160/2)
	// set the pen state
	c.t.PenDown()
	c.t.SetColor(turtle.DarkOrange)

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

// --------------------------------------------------------------------------------
//  Reacts to events from UI: change the state of the model, then update the view.
// --------------------------------------------------------------------------------

// Teleport to the requested location.
func (c *myController) jump(x, y float64) {
	c.t.SetPos(x, y)
	c.updatedPos()
	c.updatedImg()
}

// Move by the requested amount.
func (c *myController) move(d float64) {
	c.t.Forward(d)
	c.updatedPos()
	c.updatedImg()
}

// Set the heading to the requested orientation.
func (c *myController) setOri(d float64) {
	c.t.SetHeading(d)
	c.updatedOri()
	c.updatedImg()
}

// Rotate by the requested amount.
func (c *myController) rotate(d float64) {
	c.t.Left(d)
	c.updatedOri()
	c.updatedImg()
}

// Save the current world to file.
func (c *myController) save(s string) {
	c.w.SaveImage(s)
}

// Change the pen color.
func (c *myController) setPenColor(o color.Color) {
	c.t.SetColor(o)
	c.updatedPenColor()
}

// Set the pen state.
func (c *myController) setPenState(b bool) {
	if b {
		c.t.PenDown()
	} else {
		c.t.PenUp()
	}
}

// Toggle the pen state.
func (c *myController) togglePenState() {
	c.t.PenToggle()
	c.updatedPenState()
}

// Change the pen size.
func (c *myController) setPenSize(f float64) {
	c.t.SetSize(int(math.Round(f)))
	c.updatedPenSize()
}

// Create a fresh image.
func (c *myController) reset(w, h int, rc color.Color) {
	c.w.ResetImageWithSizeColor(w, h, rc)
	c.updatedImg()
}

// Draw a fractal.
func (c *myController) drawFractal(segLen float64, level int, tag string) {

	// set up the instruction stream
	instructions := make(chan turtle.Instruction)
	switch tag {
	case "hilbert":
		go fractal.GenerateHilbert(level, instructions, segLen)
	case "dragon":
		go fractal.GenerateDragon(level, instructions, segLen)
	case "sierpTri":
		go fractal.GenerateSierpinskiTriangle(level, instructions, segLen)
	case "sierpArrow":
		go fractal.GenerateSierpinskiArrowhead(level, instructions, segLen)
	}

	// draw the fractal
	for i := range instructions {
		c.t.DoInstruction(i)
		c.updatedImg()
		c.updatedPos()
		c.updatedOri()
	}
}

// --------------------------------------------------------------------------------
//  Reacts to change of the state model: update the view accordingly.
// --------------------------------------------------------------------------------

// Update all the view elements.
func (c *myController) initAll() {
	c.updatedPos()
	c.updatedOri()
	c.updatedImg()
	c.updatedPenColor()
	c.updatedPenSize()
}

// The position has been updated.
func (c *myController) updatedPos() {
	c.a.s.updatePos(c.t.X, c.t.Y)
}

// The orientation has been updated.
func (c *myController) updatedOri() {
	c.a.s.updateOri(c.t.Deg)
}

// The world image has been updated.
func (c *myController) updatedImg() {
	c.a.updateImg(c.w.Image)
}

// The pen color has been updated.
func (c *myController) updatedPenColor() {
	c.a.s.updatePenColor(c.t.Color)
}

// The pen size has been updated.
func (c *myController) updatedPenSize() {
	c.a.s.updatePenSize(c.t.Size)
}

// The pen state has been updated.
func (c *myController) updatedPenState() {
	c.a.s.updatePenState(c.t.On)
}
