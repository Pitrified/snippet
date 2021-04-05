package turtle

import "image/color"

////////////////////////////////////////////////////////////////////////////////
// A Turtle with a Pen attached
type TurtlePen struct {
	Turtle
	Pen
}

func NewTurtlePen() *TurtlePen {
	tp := &TurtlePen{Turtle{}, Pen{}}
	tp.SetColor(White)
	return tp
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
