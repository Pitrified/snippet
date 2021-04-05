package turtle

import "math"

// https://en.wikipedia.org/wiki/Turtle_graphics
// https://docs.python.org/3.9/library/turtle.html
// turtle.right(25), and it rotates in-place 25 degrees clockwise.
// standard mode
//   0 - east
//  90 - north
// 180 - west
// 270 - south
// https://goplay.space/#61SJKVrWwj

// only the agent moving around
// no world size limits, no pen those would be in a separate TurtleWorld struct
// that contains the Turtle(s)
// the reference system is a standard cartesian with origin at bottom-left:
// when drawing, the y will be changed by the TurtleWorld as needed to
// translate in origin at top-left
type Turtle struct {
	Pos Position
	Ori Orientation
}

////////////////////////////////////////////////////////////////////////////////
// Set - reset
func (t *Turtle) SetPos(pos Position) {
	t.Pos = pos
}

func (t *Turtle) ResetPos() {
	t.SetPos(Position{0, 0})
}

func (t *Turtle) SetHeading(deg float64) {
	t.Ori.SetOriDeg(deg)
}

func (t *Turtle) ResetHeading() {
	t.SetHeading(0)
}

func (t *Turtle) SetHeadingRad(rad float64) {
	t.Ori.SetOriRad(rad)
}

////////////////////////////////////////////////////////////////////////////////
// Movements
func (t *Turtle) Forward(dist float64) {
	t.Pos.X += dist * math.Sin(t.Ori.Radians)
	t.Pos.Y += dist * math.Cos(t.Ori.Radians)
}

func (t *Turtle) Backward(dist float64) {
	t.Forward(-dist)
}

// counter clockwise
func (t *Turtle) Left(deg float64) {
	t.Ori.SetOriDeg(t.Ori.Degrees + deg)
}

// if you really need to change the angle in radians...
func (t *Turtle) LeftRad(rad float64) {
	t.Left(rad2deg(rad))
}

// clockwise
func (t *Turtle) Rigth(deg float64) {
	t.Left(-deg)
}

func (t *Turtle) RigthRad(rad float64) {
	t.Rigth(rad2deg(rad))
}

////////////////////////////////////////////////////////////////////////////////
// Position
type Position struct {
	X, Y float64
}

////////////////////////////////////////////////////////////////////////////////
// Orientation
type Orientation struct {
	Degrees, Radians float64
}

func (o *Orientation) SetOriDeg(deg float64) {
	o.Degrees = deg
	o.Radians = deg2rad(deg)
}

func (o *Orientation) SetOriRad(rad float64) {
	o.Degrees = rad2deg(rad)
	o.Radians = rad
}

func deg2rad(deg float64) float64 {
	return deg * math.Pi / 180
}

func rad2deg(rad float64) float64 {
	return rad / math.Pi * 180
}
