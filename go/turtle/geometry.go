package turtle

////////////////////////////////////////////////////////////////////////////////
// Position
type Position struct {
	X, Y float64
}

func NewPositionInt(x, y int) Position {
	return Position{float64(x), float64(y)}
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
