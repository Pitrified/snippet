package turtle

import (
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"os"
)

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
	Image     *image.RGBA
	ImgHeight int

	Tp TurtlePen
}

func NewTurtleWorld(width, height int) *TurtleWorld {
	img := image.NewRGBA(image.Rect(0, 0, width, height))
	draw.Draw(img, img.Bounds(), &image.Uniform{SoftBlack}, image.Point{0, 0}, draw.Src)
	return NewTurtleWorldImage(img)
}

func NewTurtleWorldImage(m *image.RGBA) *TurtleWorld {
	tp := *NewTurtlePen()
	return &TurtleWorld{
		Image:     m,
		ImgHeight: m.Bounds().Max.Y,
		Tp:        tp,
	}
}

////////////////////////////////////////////////////////////////////////////////
// Set - reset
func (tw *TurtleWorld) SetPos(pos Position) {
	startPos := tw.Tp.Pos
	tw.Tp.SetPos(pos)
	endPos := tw.Tp.Pos
	if tw.Tp.On {
		tw.drawLineBresenham(startPos, endPos)
	}
}

func (tw *TurtleWorld) SetHeading(deg float64) {
	tw.Tp.SetHeading(deg)
}

////////////////////////////////////////////////////////////////////////////////
// Movements
func (tw *TurtleWorld) Forward(dist float64) {
	startPos := tw.Tp.Pos
	tw.Tp.Forward(dist)
	endPos := tw.Tp.Pos
	if tw.Tp.On {
		tw.drawLineBresenham(startPos, endPos)
	}
}

func (tw *TurtleWorld) Backward(dist float64) {
	tw.Forward(-dist)
}

func (tw *TurtleWorld) Left(deg float64) {
	tw.Tp.Left(deg)
}

func (tw *TurtleWorld) Rigth(deg float64) {
	tw.Left(-deg)
}

////////////////////////////////////////////////////////////////////////////////
// Pen/colors
func (tw *TurtleWorld) PenUp() {
	tw.Tp.PenUp()
}

func (tw *TurtleWorld) PenDown() {
	tw.Tp.PenDown()
}

func (tw *TurtleWorld) SetColor(c color.Color) {
	tw.Tp.SetColor(c)
}

////////////////////////////////////////////////////////////////////////////////
// Drawing

// Bresenham
// https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm#Algorithm_for_integer_arithmetic
func (tw *TurtleWorld) drawLineBresenham(startPos, endPos Position) {

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
			tw.SetPixel(x0, i)
		}
		return
	}

	// line is horizontal
	if y0 == y1 {
		if x0 > x1 {
			x1, x0 = x0, x1
		}
		for i := x0; i <= x1; i++ {
			tw.SetPixel(i, y0)
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
		tw.SetPixel(x0, y0)
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

// Draw in different reference frame
func (tw *TurtleWorld) SetPixel(x, y int) {
	yr := tw.ImgHeight - y
	tw.Image.Set(x, yr, tw.Tp.Color)

	// this color should be slightly less bright
	cMid := tw.Tp.Color
	tw.Image.Set(x+1, yr, cMid)
	tw.Image.Set(x-1, yr, cMid)
	tw.Image.Set(x, yr+1, cMid)
	tw.Image.Set(x, yr-1, cMid)

	// and this even dimmer
	cMin := tw.Tp.Color
	tw.Image.Set(x+1, yr+1, cMin)
	tw.Image.Set(x-1, yr+1, cMin)
	tw.Image.Set(x+1, yr-1, cMin)
	tw.Image.Set(x-1, yr-1, cMin)
}

////////////////////////////////////////////////////////////////////////////////
// Save output
func (tw *TurtleWorld) SaveImage(filePath string) error {
	f, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer f.Close()
	err = png.Encode(f, tw.Image)
	return err
}
