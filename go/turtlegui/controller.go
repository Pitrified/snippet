package main

import (
	"fmt"

	"github.com/Pitrified/go-turtle"
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
	c.w = turtle.NewWorld(900, 600)
	// create the turtle to control
	c.t = turtle.NewTurtleDraw(c.w)
	c.t.PenDown()

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
//  Reacts to events from UI
// --------------------------------------------------------------------------------

// The user requested a jump.
func (c *myController) jump(x, y float64) {
	fmt.Printf("CONT: jump x, y = %+v, %+v\n", x, y)
	c.t.SetPos(x, y)
	c.updatedPos()
	c.updatedImg()
}

// The user requested a movement.
func (c *myController) move(d float64) {
	fmt.Printf("CONT: move d = %+v\n", d)
	c.t.Forward(d)
	c.updatedPos()
	c.updatedImg()
}

// The user requested a orientation set.
func (c *myController) setOri(d float64) {
	fmt.Printf("CONT: rotate d = %+v\n", d)
	c.t.SetHeading(d)
	c.updatedOri()
	c.updatedImg()
}

// The user requested a rotation.
func (c *myController) rotate(d float64) {
	fmt.Printf("CONT: rotate d = %+v\n", d)
	c.t.Left(d)
	c.updatedOri()
	c.updatedImg()
}

// The user requested saving the world to file.
func (c *myController) save(s string) {
	fmt.Printf("CONT: save s = %+v\n", s)
	c.w.SaveImage(s)
}

// --------------------------------------------------------------------------------
//  Reacts to change of the state model
// --------------------------------------------------------------------------------

// Update all the view elements.
func (c *myController) initAll() {
	c.updatedPos()
	c.updatedOri()
	c.updatedImg()
}

// The position has been updated in the model: update the view accordingly.
func (c *myController) updatedPos() {
	c.a.s.updatePos(c.t.X, c.t.Y)
}

// The orientation has been updated in the model: update the view accordingly.
func (c *myController) updatedOri() {
	c.a.s.updateOri(c.t.Deg)
}

// The world image has been updated.
func (c *myController) updatedImg() {
	c.a.updateImg(c.w.Image)
}
