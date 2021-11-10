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
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
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
//  SIDEBAR
// --------------------------------------------------------------------------------

type mySidebar struct {
	a *myApp

	confCard    *widget.Card
	confTickLen *widget.Entry
	// confNAmount *WideEntry
	confNAmount *widget.Entry
	confNRadius *widget.Entry

	resCard     *widget.Card
	resReset    *widget.Button
	resCellsW   *WideEntry
	resCellsH   *widget.Entry
	resPerMin   *WideEntry
	resPerMax   *widget.Entry
	resCellSize *WideEntry
}

func newSidebar(a *myApp) *mySidebar {
	return &mySidebar{a: a}
}

// Build the sidebar.
func (s *mySidebar) buildSidebar() *container.Scroll {
	return container.NewVScroll(
		container.NewVBox(
			s.buildConfig(),
			s.buildReset(),
		),
	)
}

// ##### CONFIG #####

// Set params that do not require a reset of the world.
//
// * clockTickLen
// * nudgeAmount
// * nudgeRadius
// * blinkCooldown
// * drawCheckerboard
// * interact fireflies
func (s *mySidebar) buildConfig() *widget.Card {

	// clockTickLen entry
	s.confTickLen = widget.NewEntry()
	s.confTickLen.Text = "25"
	s.confTickLen.OnSubmitted = s.confConfigSubmitted
	contClockLen := container.NewBorder(
		nil, nil, widget.NewLabel("Tick length:"), widget.NewLabel("ms"),
		s.confTickLen,
	)

	// nudge
	s.confNAmount = widget.NewEntry()
	s.confNAmount.Text = "50"
	s.confNAmount.OnSubmitted = s.confConfigSubmitted
	s.confNRadius = widget.NewEntry()
	s.confNRadius.Text = "20"
	s.confNRadius.OnSubmitted = s.confConfigSubmitted
	contNudge := container.NewBorder(
		nil, nil, widget.NewLabel("Nudge:"), nil,
		container.NewGridWithColumns(2,
			container.NewBorder(
				nil, nil, widget.NewLabel("By:"), widget.NewLabel("ms"),
				s.confNAmount,
			),
			container.NewBorder(
				nil, nil, widget.NewLabel("Radius:"), widget.NewLabel("px"),
				s.confNRadius,
			),
		),
	)

	contCard := container.NewVBox(contClockLen, contNudge)
	s.confCard = widget.NewCard("Config", "", contCard)
	return s.confCard
}

// Pressed enter on any entry in the world config card.
func (s *mySidebar) confConfigSubmitted(_ string) {
	s.a.configWorld()
}

// ##### RESET #####

// Set params that require a reset of the world.
//
// * CellW/CellH/CellSize
// * Period
func (s *mySidebar) buildReset() *widget.Card {

	// button to reset world
	s.resReset = widget.NewButton("Reset", s.resResetCB)

	// entries to set world size in cells
	// Entry W, at least wide 3*IconInlineSize
	s.resCellsW = NewWideEntry(fyne.NewSize(3*theme.IconInlineSize(), 0))
	s.resCellsW.Text = "3"
	s.resCellsW.OnSubmitted = s.resResetSubmitted
	// Entry H, the width is set equal to W by the grid layout
	s.resCellsH = widget.NewEntry()
	s.resCellsH.Text = "3"
	s.resCellsH.OnSubmitted = s.resResetSubmitted
	contCells := container.NewBorder(
		nil, nil, widget.NewLabel("World size:"), widget.NewLabel("cells"),
		container.NewGridWithColumns(2,
			container.NewBorder(
				nil, nil, widget.NewLabel("W:"), nil,
				s.resCellsW,
			),
			container.NewBorder(
				nil, nil, widget.NewLabel("H:"), nil,
				s.resCellsH,
			),
		),
	)

	// cell size
	s.resCellSize = NewWideEntry(fyne.NewSize(3*theme.IconInlineSize(), 0))
	s.resCellSize.Text = "100"
	s.resCellSize.OnSubmitted = s.resResetSubmitted
	contSize := container.NewBorder(
		nil, nil, widget.NewLabel("Cell size:"), widget.NewLabel("pixels"),
		s.resCellSize,
	)

	// period controls
	s.resPerMin = NewWideEntry(fyne.NewSize(3*theme.IconInlineSize(), 0))
	s.resPerMin.Text = "900"
	s.resPerMin.OnSubmitted = s.resResetSubmitted
	s.resPerMax = widget.NewEntry()
	s.resPerMax.Text = "1100"
	s.resPerMax.OnSubmitted = s.resResetSubmitted
	contPer := container.NewBorder(
		nil, nil, widget.NewLabel("Period:"), widget.NewLabel("ms"),
		container.NewGridWithColumns(2,
			container.NewBorder(
				nil, nil, widget.NewLabel("Min:"), nil,
				s.resPerMin,
			),
			container.NewBorder(
				nil, nil, widget.NewLabel("Max:"), nil,
				s.resPerMax,
			),
		),
	)

	contCard := container.NewVBox(contCells, contSize, contPer, s.resReset)
	s.resCard = widget.NewCard("Reset", "", contCard)
	return s.resCard
}

// Clicked button reset world.
func (s *mySidebar) resResetCB() {
	s.a.resetWorld()
}

// Pressed enter on any entry in the world reset card.
func (s *mySidebar) resResetSubmitted(_ string) {
	s.a.resetWorld()
}

// --------------------------------------------------------------------------------
//  APP
// --------------------------------------------------------------------------------

type myApp struct {
	fyneApp fyne.App
	mainWin fyne.Window

	s *mySidebar

	w         *cellfire.World // World to render.
	wImg      *canvas.Image   // Canvas to render the world on.
	wSize     image.Rectangle // Size of the world.
	wCellWG   sync.WaitGroup  // WG to communicate that the rendering of the cell is done.
	wCellSize int             // Size of each cell as int.
	wCellW    int             // Width of the world in cells.
	wCellH    int             // Height of the world in cells.

	clockTickLen  int
	nudgeAmount   int
	nudgeRadius   float32
	blinkCooldown int
	periodMin     int
	periodMax     int

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

	cellfire.PrinterInit(10000)

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

	a.s = newSidebar(a)
	contSidebar := a.s.buildSidebar()

	borderCont := container.NewBorder(nil, nil, contSidebar, nil,
		a.wImg,
	)

	a.mainWin.SetContent(borderCont)
}

// Reset the world to simulate.
//
// Get all the values from the current UI state.
func (a *myApp) resetWorld() {
	a.wCellW = 16
	a.wCellH = 16
	a.wCellSize = 100
	clockStart := 1_000_000
	a.clockTickLen = 25_000
	a.nudgeAmount = 100_000
	a.nudgeRadius = 50
	a.blinkCooldown = 500_000
	a.periodMin = 900_000
	a.periodMax = 1_100_000
	a.w = cellfire.NewWorld(
		a.wCellW, a.wCellH, float32(a.wCellSize),
		clockStart, a.clockTickLen,
		a.nudgeAmount, a.nudgeRadius,
		a.blinkCooldown,
		a.periodMin, a.periodMax,
	)
	nF := 10000
	a.w.HatchFireflies(nF)

	// size of the image to render the world in
	// MAYBE needs a -1 on the right/top border
	a.wSize = image.Rect(0, 0, a.wCellW*a.wCellSize, a.wCellH*a.wCellSize)

}

// Update the world with the new params.
func (a *myApp) configWorld() {
}

func (a *myApp) runApp() {
	a.buildUI()
	a.resetWorld()
	a.animate()
	a.mainWin.Resize(fyne.NewSize(1200, 900))
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
			// a.w.DoStep <- 'M'
			a.w.Move()
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

	// // checkerboard pattern
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
	theApp.runApp()
}
