package turtle

import (
	"image"
	"image/color"
)

////////////////////////////////////////////////////////////////////////////////
// A Turtle with a Pen attached
type TurtlePen struct {
	*Turtle
	*Pen
}

////////////////////////////////////////////////////////////////////////////////
// A Pen with a color and a state
type Pen struct {
	Color color.Color
	On    bool
}

func (p *Pen) PenUp() {
	p.On = false
}

func (p *Pen) PenDown() {
	p.On = true
}

func (p *Pen) SetColor(c color.Color) {
	p.Color = c
}

func NewTurtlePen() *TurtlePen {
	tp := &TurtlePen{}
	tp.Color = color.White
	return tp
}

////////////////////////////////////////////////////////////////////////////////
// A World with a TurtlePen
// MAYBEnot you set the CURRENT TurtlePen to use then you can have as many as
// you want, and just call SetActiveTurtlePen and then
// call TurtleWorld.Forward(10) and it will magically move that and draw the
// line using that TurtlePen
// if we had constructor it would be saner, use
// NewTurtleWorld(m) to generate a brand new TurtlePen
// NewTurtleWorldEmpty(w, h, background) to generate a brand new TurtlePen and Image
// NewTurtleWorldWithPen(m, tp) to set tp as active
type TurtleWorld struct {
	Image *image.RGBA
	Tp    TurtlePen
}

func NewTurtleWorld(m *image.RGBA) *TurtleWorld {
	tp := *NewTurtlePen()
	return &TurtleWorld{
		Image: m,
		Tp:    tp,
	}
}

func (tw *TurtleWorld) Forward(dist float64) {
	startPos := tw.Tp.Pos
	tw.Tp.Forward(dist)
	endPos := tw.Tp.Pos
	drawLineBresenham(tw.Image, tw.Tp.Color, startPos, endPos)
}

// Bresenham
// https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm#Algorithm_for_integer_arithmetic
func drawLineBresenham(m *image.RGBA, c color.Color, startPos, endPos Position) {

	x0 := int(startPos.X)
	y0 := int(startPos.Y)
	x1 := int(endPos.X)
	y1 := int(endPos.Y)

	// line is vertical
	if x0 == x1 {
		if y0 > y1 {
			y1, y0 = y0, y1
		}
		for i := y0; i <= y1; i++ {
			m.Set(x0, i, c)
		}
		return
	}

	// line is horizontal
	if y0 == y1 {
		if x0 > x1 {
			x1, x0 = x0, x1
		}
		for i := x0; i <= x1; i++ {
			m.Set(i, y0, c)
		}
		return
	}

	// line is diagonal, draw it with Bresenham algo
	dx := intAbs(x1 - x0)
	dy := -intAbs(y1 - y0)
	var sx, sy int
	if x0 < x1 {
		sx = 1
	} else {
		sx = -1
	}
	if y0 < y1 {
		sy = 1
	} else {
		sy = -1
	}
	err := dx + dy

	var e2 int
	for {
		m.Set(x0, y0, c)
		if x0 == x1 && y0 == y1 {
			return
		}
		e2 = 2 * err
		if e2 >= dy {
			err += dy
			x0 += sx
		}
		if e2 <= dx {
			err += dx
			y0 += sy
		}
	}
}
