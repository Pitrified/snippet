package main

import (
	"blinker/cellfire"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"math"
	"sync"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
)

// --------------------------------------------------------------------------------
//  MISC
// --------------------------------------------------------------------------------

// brightness goes from 1 to 0, according to decay constant
// tau = 1 / decay
// https://www.wolframalpha.com/input/?i=e+**+%28+-x+*+1%2F50+%29+for+0+%3C+x+%3C+250
func brightness(x int, decay float64) float64 {
	if x < 0 {
		return 0
	}
	return math.Exp(-float64(x) * decay)
}

// --------------------------------------------------------------------------------
//  APP
// --------------------------------------------------------------------------------

type myApp struct {
	fyneApp fyne.App
	mainWin fyne.Window

	w         *cellfire.World // World to render.
	wImg      *canvas.Image   // Canvas to render the world on.
	wSize     image.Rectangle // Size of the world.
	wCellWG   sync.WaitGroup  // WG to communicate that the rendering of the cell is done.
	wCellSize int             // Size of each cell as int.
	wCellW    int             // Width of the world in cells.
	wCellH    int             // Height of the world in cells.

	decay float64 // Decay rate of the brightness since the blink.
}

// Create a new app.
func newApp() *myApp {

	// create the app
	fyneApp := app.New()
	mainWin := fyneApp.NewWindow("Blinking fireflies")
	a := &myApp{fyneApp: fyneApp, mainWin: mainWin}

	// add the link for typed runes
	a.mainWin.Canvas().SetOnTypedKey(a.typedKey)

	// create the world to simulate
	a.wCellW = 3
	a.wCellH = 3
	a.wCellSize = 100
	a.w = cellfire.NewWorld(a.wCellW, a.wCellH, float32(a.wCellSize))
	nF := 500
	a.w.HatchFireflies(nF)

	cellfire.PrinterInit(100)

	// size of the image to render the world in
	// MAYBE needs a -1 on the right/top border
	a.wSize = image.Rect(0, 0, a.wCellW*a.wCellSize, a.wCellH*a.wCellSize)

	a.decay = 1.0 / 600_000.0

	return a
}

func (a *myApp) buildUI() {

	m := image.NewRGBA(image.Rect(0, 0, 400, 300))
	draw.Draw(
		m, m.Bounds(),
		&image.Uniform{color.RGBA{10, 10, 10, 255}},
		image.Point{0, 0},
		draw.Src,
	)
	a.wImg = canvas.NewImageFromImage(m)
	a.wImg.FillMode = canvas.ImageFillContain
	a.wImg.SetMinSize(fyne.NewSize(400, 400))

	borderCont := container.NewBorder(nil, nil, nil, nil,
		a.wImg,
	)

	a.mainWin.SetContent(borderCont)
}

func (a *myApp) runApp() {
	a.mainWin.Resize(fyne.NewSize(900, 900))
	a.mainWin.Show()
	a.fyneApp.Run()
}

func (a *myApp) animate() {
	go func() {
		// Render rate limiter
		tickRender := time.NewTicker(time.Second / 25)

		// for { select { case <-tickRender.C: } }
		for range tickRender.C {
			a.renderWorld()
			// a.w.Move()
			// a.w.DoStep <- 'M'
			a.w.ClockTick()
		}

	}()
}

func (a *myApp) typedKey(ev *fyne.KeyEvent) {
	fmt.Printf("typedKey  = %+v %T\n", ev, ev)
	switch ev.Name {
	case fyne.KeyEscape, fyne.KeyQ:
		a.fyneApp.Quit()
	default:
	}
}

// --------------------------------------------------------------------------------
//  RENDERING
// --------------------------------------------------------------------------------

// Render the World as an image, and update the canvas.
func (a *myApp) renderWorld() {
	img := image.NewRGBA(a.wSize)

	draw.Draw(
		img, img.Bounds(),
		&image.Uniform{color.RGBA{10, 10, 10, 255}},
		image.Point{0, 0},
		draw.Src,
	)

	for i := 0; i < a.w.CellWNum; i++ {
		for ii := 0; ii < a.w.CellHNum; ii++ {
			a.wCellWG.Add(1)
			go a.renderCell(a.w.Cells[i][ii], img)
		}
	}
	a.wCellWG.Wait()

	a.wImg.Image = img
	a.wImg.Refresh()
}

// Render the cell.
func (a *myApp) renderCell(c *cellfire.Cell, m *image.RGBA) {

	// checkerboard pattern
	// left := c.Cx * a.wCellSize
	// bottom := c.Cy * a.wCellSize
	// col := uint8(20)
	// if c.Cx%2 == c.Cy%2 {
	// 	col = 30
	// }
	// for i := 0; i < a.wCellSize; i++ {
	// 	for ii := 0; ii < a.wCellSize; ii++ {
	// 		m.Set(left+i, bottom+ii, color.RGBA{col, col, col, 255})
	// 	}
	// }

	minBr := 60.0
	fCol := color.RGBA{10, 10, uint8(minBr), 255}
	for _, f := range c.Fireflies {
		since := a.w.Clock - (f.NextBlink - f.Period)
		br := brightness(since, a.decay)
		brightMax := uint8((255-minBr)*br + minBr)
		fCol.R = brightMax
		fCol.G = brightMax
		m.Set(int(f.X), int(f.Y), fCol)
	}

	a.wCellWG.Done()
}

// --------------------------------------------------------------------------------
//  MAIN
// --------------------------------------------------------------------------------

func main() {
	theApp := newApp()
	theApp.buildUI()
	theApp.animate()
	theApp.runApp()
}
