package main

import (
	"fmt"
	"image"
	"image/color"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/driver/desktop"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
)

const (
	cellSize = 8
)

type gameRenderer struct {
	render   *canvas.Raster
	objects  []fyne.CanvasObject
	imgCache *image.RGBA

	aliveColor color.Color
	deadColor  color.Color

	game *game
}

// compliant with WidgetRenderer interface
// https://pkg.go.dev/fyne.io/fyne/v2#WidgetRenderer
var _ fyne.WidgetRenderer = &gameRenderer{}

func (gr *gameRenderer) MinSize() fyne.Size {
	pixDensity := gr.game.pixelDensity()
	return fyne.NewSize(float32(minXCount*cellSize)/pixDensity, float32(minYCount*cellSize)/pixDensity)
}

func (gr *gameRenderer) Layout(size fyne.Size) {
	fmt.Printf("Layout = %+v\n", size)
	gr.render.Resize(size)
}

func (gr *gameRenderer) ApplyTheme() {
	gr.aliveColor = theme.ForegroundColor()
	gr.deadColor = theme.BackgroundColor()
}

func (gr *gameRenderer) BackgroundColor() color.Color {
	return theme.BackgroundColor()
}

func (gr *gameRenderer) Refresh() {
	fmt.Println("Refresh start")
	canvas.Refresh(gr.render)
	fmt.Println("Refresh end")
}

func (gr *gameRenderer) Objects() []fyne.CanvasObject {
	return gr.objects
}

func (gr *gameRenderer) Destroy() {
}

func (gr *gameRenderer) draw(w, h int) image.Image {
	fmt.Printf("draw : w, h = %+v %+v\n", w, h)
	pixDensity := gr.game.pixelDensity()
	pixW, pixH := gr.game.cellForCoord(w, h, pixDensity)

	img := gr.imgCache
	if img == nil || img.Bounds().Size().X != pixW || img.Bounds().Size().Y != pixH {
		img = image.NewRGBA(image.Rect(0, 0, pixW, pixH))
		gr.imgCache = img
	}
	gr.game.board.ensureGridSize(pixW, pixH)

	for y := 0; y < pixH; y++ {
		for x := 0; x < pixW; x++ {
			if x < gr.game.board.width && y < gr.game.board.height && gr.game.board.cells[y][x] {
				img.Set(x, y, gr.aliveColor)
			} else {
				img.Set(x, y, gr.deadColor)
			}
		}
	}

	return img
}

type game struct {
	widget.BaseWidget

	genText *widget.Label
	board   *board
	paused  bool
}

// compliant with Widget interface
// https://pkg.go.dev/fyne.io/fyne/v2#Widget
var _ fyne.Widget = &game{}

func (g *game) CreateRenderer() fyne.WidgetRenderer {
	fmt.Println("Starting CreateRenderer")
	renderer := &gameRenderer{game: g}
	fmt.Println("Created gameRenderer")

	render := canvas.NewRaster(renderer.draw)
	render.ScaleMode = canvas.ImageScalePixels
	renderer.render = render
	renderer.objects = []fyne.CanvasObject{render}
	renderer.ApplyTheme()

	return renderer
}

func (g *game) cellForCoord(x, y int, density float32) (int, int) {
	xpos := int(float32(x) / float32(cellSize) / density)
	ypos := int(float32(y) / float32(cellSize) / density)

	return xpos, ypos
}

func (g *game) Run() {
	g.paused = false
}

func (g *game) Stop() {
	g.paused = true
}

func (g *game) toggleRun() {
	g.paused = !g.paused
}

func (g *game) animate() {
	go func() {
		tick := time.NewTicker(time.Second / 6)

		for range tick.C {

			if g.paused {
				continue
			}

			g.board.nextGen()
			g.updateGeneration()
			g.Refresh()
		}

		// for {
		// 	select {
		// 	case
		// }
	}()
}

func (g *game) typedRune(r rune) {
	if r == ' ' {
		g.toggleRun()
	}
}

func (g *game) Tapped(ev *fyne.PointEvent) {
	pixDensity := g.pixelDensity()
	xpos, ypos := g.cellForCoord(int(ev.Position.X*pixDensity), int(ev.Position.Y*pixDensity), pixDensity)

	if ev.Position.X < 0 || ev.Position.Y < 0 || xpos >= g.board.width || ypos >= g.board.height {
		return
	}

	g.board.cells[ypos][xpos] = !g.board.cells[ypos][xpos]

	g.Refresh()
}

func (g *game) TappedSecondary(ev *fyne.PointEvent) {
	fmt.Printf("TappedSecondary ev = %+v\n", ev)
}

// https://developer.fyne.io/api/v2.0/driver/desktop/mouseable.html
func (g *game) MouseDown(ev *desktop.MouseEvent) {
	fmt.Printf("MouseDown ev = %+v\n", ev)
}

func (g *game) MouseUp(ev *desktop.MouseEvent) {
	fmt.Printf("MouseUp ev = %+v\n", ev)
}

// https://developer.fyne.io/api/v2.0/driver/desktop/hoverable.html
func (g *game) MouseIn(ev *desktop.MouseEvent) {
	fmt.Printf("MouseIn ev = %+v\n", ev)
}

func (g *game) MouseMoved(ev *desktop.MouseEvent) {
	fmt.Printf("MouseMoved ev = %+v\n", ev)
}

func (g *game) MouseOut() {
	fmt.Print("MouseOut\n")
}

// canvas Scrollable interface
func (g *game) Scrolled(ev *fyne.ScrollEvent) {
	fmt.Printf("Scrolled ev = %+v\n", ev)
}

func (g *game) buildUI() fyne.CanvasObject {
	var pause *widget.Button
	pause = widget.NewButton("Pause", func() {
		g.paused = !g.paused

		if g.paused {
			pause.SetText("Resume")
		} else {
			pause.SetText("Pause")
		}
	})

	title := container.New(layout.NewGridLayout(2), g.genText, pause)
	return container.New(layout.NewBorderLayout(title, nil, nil, nil), title, g)
}

func (g *game) updateGeneration() {
	g.genText.SetText(fmt.Sprintf("Generation %d", g.board.generation))
}

func (g *game) pixelDensity() float32 {
	c := fyne.CurrentApp().Driver().CanvasForObject(g)
	if c == nil {
		return 1.0
	}

	pixW, _ := c.PixelCoordinateForPosition(fyne.NewPos(cellSize, cellSize))
	return float32(pixW) / float32(cellSize)
}

func newGame(b *board) *game {
	fmt.Println("Starting newGame")
	g := &game{board: b, genText: widget.NewLabel("Generation 0")}
	fmt.Println("Created game")
	g.ExtendBaseWidget(g)
	fmt.Println("Done ExtendBaseWidget")

	return g
}
