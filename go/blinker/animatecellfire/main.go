package main

import (
	"blinker/cellfire"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"math"
	"math/rand"
	"strconv"
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

	confCard     *widget.Card
	confApply    *widget.Button
	confFireNum  *widget.Entry
	confTickLen  *widget.Entry
	confBliCool  *widget.Entry
	confNAmount  *widget.Entry
	confNRadius  *widget.Entry
	confDrawGrid *widget.Check
	confInteract *widget.Check
	confRequest  bool

	resCard     *widget.Card
	resReset    *widget.Button
	resCellsW   *WideEntry
	resCellsH   *widget.Entry
	resPerMin   *WideEntry
	resPerMax   *widget.Entry
	resCellSize *WideEntry
	resRequest  bool
}

func newSidebar(a *myApp) *mySidebar {
	return &mySidebar{a: a}
}

// Build the sidebar.
func (s *mySidebar) buildSidebar() *container.Scroll {
	contSidebar := container.NewVScroll(
		container.NewVBox(
			s.buildConfig(),
			s.buildReset(),
		),
	)
	return contSidebar
}

// Conlcude the setup of the sidebar widget.
func (s *mySidebar) initSidebar() {
	// we can only init this after the build is done
	// the callback needs all widget to exist
	s.confInteract.SetChecked(true)
}

// ##### CONFIG #####

// Set params that do not require a reset of the world.
//
// * firefly amount
// * clockTickLen
// * nudgeAmount
// * nudgeRadius
// * blinkCooldown
// * drawCheckerboard
// * interact fireflies
func (s *mySidebar) buildConfig() *widget.Card {

	// draw grid - interact fireflies
	s.confDrawGrid = widget.NewCheck("Draw grid", s.confConfigChecked)
	s.confInteract = widget.NewCheck("Interaction", s.confConfigChecked)

	// button to reset world
	s.confApply = widget.NewButton("Apply", s.confApplyCB)

	// clockTickLen entry
	s.confTickLen = widget.NewEntry()
	s.confTickLen.Text = "25"
	s.confTickLen.OnSubmitted = s.confConfigSubmitted
	// contClockLen := container.NewBorder( nil, nil, widget.NewLabel("Tick length:"), widget.NewLabel("ms"), s.confTickLen)

	// blinkCooldown entry
	s.confBliCool = widget.NewEntry()
	s.confBliCool.Text = "500"
	s.confBliCool.OnSubmitted = s.confConfigSubmitted
	// contBlinkCooldown := container.NewBorder(nil, nil, widget.NewLabel("Blink cooldown:"), widget.NewLabel("ms"), s.confBliCool)

	// number of fireflies entry
	s.confFireNum = widget.NewEntry()
	// s.confFireNum.Text = "40000"
	s.confFireNum.Text = "2000"
	s.confFireNum.OnSubmitted = s.confConfigSubmitted
	contFireNum := container.NewBorder(
		nil, nil, widget.NewLabel("Fireflies:"), s.confInteract,
		s.confFireNum,
	)

	// nudge
	// TODO sliders are a lot better
	s.confNAmount = widget.NewEntry()
	s.confNAmount.Text = "20"
	s.confNAmount.OnSubmitted = s.confConfigSubmitted
	s.confNRadius = widget.NewEntry()
	// s.confNRadius.Text = "30"
	s.confNRadius.Text = "25"
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

	contCard := container.NewVBox(
		contFireNum,
		contNudge,
		// contClockLen,
		// contBlinkCooldown,
		s.confDrawGrid,
		s.confApply,
	)
	s.confCard = widget.NewCard("Config", "", contCard)
	return s.confCard
}

// Pressed button to apply config changes.
func (s *mySidebar) confApplyCB() {
	s.confRequest = true
}

// Pressed enter on any entry in the world config card.
func (s *mySidebar) confConfigSubmitted(_ string) {
	s.confRequest = true
}

// Checked any checkbutton in the world config card.
func (s *mySidebar) confConfigChecked(state bool) {
	s.confRequest = true
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
	// s.resCellsW.Text = "16"
	s.resCellsW.Text = "4"
	s.resCellsW.OnSubmitted = s.resResetSubmitted
	// Entry H, the width is set equal to W by the grid layout
	s.resCellsH = widget.NewEntry()
	// s.resCellsH.Text = "16"
	s.resCellsH.Text = "4"
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
	s.resRequest = true
}

// Pressed enter on any entry in the world reset card.
func (s *mySidebar) resResetSubmitted(_ string) {
	s.resRequest = true
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
	nF            int
	nFold         int
	newFId        int

	decay         float64 // Decay rate of the brightness since the blink.
	drawGrid      bool    // Draw the cell grid.
	doInteraction bool    // Do the interactions between fireflies.
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

	// // for the first reset to work we need this placeholder values
	// // will be set to the correct ones in the first reset
	// a.nudgeAmount = 100_000
	// a.nudgeRadius = 20
	// a.nF = 400

}

// Reset the world to simulate.
//
// Get all the values from the current UI state.
func (a *myApp) resetWorld() {

	// read only from UI to load the values
	a.configRead("reset")

	// get the reset params from the UI
	a.resetRead()

	// create a new world
	a.w = cellfire.NewWorld(
		a.wCellW, a.wCellH, float32(a.wCellSize),
		1_000_000, a.clockTickLen,
		a.nudgeAmount, a.nudgeRadius,
		a.blinkCooldown,
		a.periodMin, a.periodMax,
	)
	a.w.HatchFireflies(a.nF)
	a.newFId = a.nF + 1

	// mark the request as done
	a.s.resRequest = false
	a.s.confRequest = false

	// update the config params
	a.configApply("reset")
}

// Read the reset params from the UI
func (a *myApp) resetRead() {

	cW, cWerr := strconv.Atoi(a.s.resCellsW.Text)
	cH, cHerr := strconv.Atoi(a.s.resCellsH.Text)
	cS, cSerr := strconv.Atoi(a.s.resCellSize.Text)
	pMin, pMinerr := strconv.Atoi(a.s.resPerMin.Text)
	pMax, pMaxerr := strconv.Atoi(a.s.resPerMax.Text)
	if cWerr != nil || cHerr != nil || cSerr != nil || pMinerr != nil || pMaxerr != nil {
		return
	}

	a.wCellW = cW
	a.wCellH = cH
	a.wCellSize = cS
	a.periodMin = pMin * 1000
	a.periodMax = pMax * 1000

	// size of the image to render the world in
	// MAYBE needs a -1 on the right/top border
	a.wSize = image.Rect(0, 0, a.wCellW*a.wCellSize, a.wCellH*a.wCellSize)

}

// Update the world with the new config params.
//
// Extract the data from the UI and update the world.
func (a *myApp) configWorld(source string) {
	a.configRead("config")
	a.configApply("config")
}

// Extract the data from the UI.
func (a *myApp) configRead(source string) {

	// from checkbox
	a.drawGrid = a.s.confDrawGrid.Checked
	a.doInteraction = a.s.confInteract.Checked

	// get data from entries
	nF, nFerr := strconv.Atoi(a.s.confFireNum.Text)
	nA, nAerr := strconv.Atoi(a.s.confNAmount.Text)
	nR, nRerr := strconv.Atoi(a.s.confNRadius.Text)
	if nFerr != nil || nAerr != nil || nRerr != nil {
		return
	}
	// fmt.Printf("nF, nA, nR = %+v %+v %+v\n", nF, nA, nR)

	// save data in the app
	a.nudgeAmount = nA * 1000
	// to stop the interaction set the redius to 0
	if a.doInteraction {
		a.nudgeRadius = float32(nR)
	} else {
		a.nudgeRadius = 0
	}

	// constants for now, too confusing for the user
	a.clockTickLen = 25_000
	a.blinkCooldown = 500_000

	switch source {
	case "reset":
		// if we reset, also set old to nF
		// the new world created will respect the requested value
		a.nFold = nF
		a.nF = nF
	case "config":
		// if this was a config, we need to add/remove fireflies manually
		a.nFold = a.nF
		a.nF = nF
	}
}

// Apply the configuration to the world
func (a *myApp) configApply(source string) {
	a.w.NudgeAmount = a.nudgeAmount
	a.w.NudgeRadius = a.nudgeRadius

	// add/remove fireflies
	if a.nFold != a.nF {
		a.changeFireflyNum()
	}
	a.nFold = a.nF
}

func (a *myApp) changeFireflyNum() {
	fmt.Printf("a.nFold, a.nF = %+v %+v\n", a.nFold, a.nF)

	totCNum := a.wCellW * a.wCellH

	// remove fireflies
	i := 0
	for a.nFold > a.nF {
		cId := i % totCNum
		cX := cId % a.wCellW
		cY := cId / a.wCellH
		fId := getMapKey(a.w.Cells[cX][cY].Fireflies)
		// fmt.Printf("i, cId, cX, cY, fId = %+v %+v %+v %+v %+v\n", i, cId, cX, cY, fId)
		i++
		if fId == -1 {
			continue
		}
		f := a.w.Cells[cX][cY].Fireflies[fId]
		a.w.Cells[cX][cY].Leave(f)
		a.nFold--
	}
	for a.nFold < a.nF {
		x := rand.Float32() * a.w.SizeW
		y := rand.Float32() * a.w.SizeH
		o := int16(rand.Float64() * 360)
		p := cellfire.RandRangeInt(a.w.PeriodMin, a.w.PeriodMax)
		cellfire.NewFirefly(x, y, o, a.newFId, p, a.w)
		a.newFId++
		a.nFold++
	}
}

func (a *myApp) runApp() {
	rand.Seed(time.Now().UnixNano())
	a.buildUI()
	a.resetWorld()
	a.s.initSidebar()
	go a.animate()
	a.mainWin.Resize(fyne.NewSize(1200, 900))
	a.mainWin.Show()
	a.fyneApp.Run()
}

func (a *myApp) animate() {
	// Render rate limiter
	tickRender := time.NewTicker(time.Second / 25)

	// for { select { case <-tickRender.C: } }
	for range tickRender.C {
		// evade outstanding requests
		if a.s.resRequest {
			a.resetWorld()
		} else if a.s.confRequest {
			a.configWorld("animate")
		}
		// t1 := time.Now()
		a.renderWorld()
		// t2 := time.Now()
		// a.w.DoStep <- 'M'
		a.w.Move()
		// t3 := time.Now()
		a.w.ClockTick()
		// t4 := time.Now()
		// fmt.Printf("render %+v move %+v tick %+v\n",
		// 	t2.Sub(t1),
		// 	t3.Sub(t2),
		// 	t4.Sub(t3),
		// )
	}
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
	if a.drawGrid {
		left := c.Cx * a.wCellSize
		bottom := c.Cy * a.wCellSize
		col := uint8(20)
		if c.Cx%2 == c.Cy%2 {
			col = 30
		}
		for i := 0; i < a.wCellSize; i++ {
			for ii := 0; ii < a.wCellSize; ii++ {
				m.Set(left+i, bottom+ii, color.RGBA{col, col, col, 255})
			}
		}
	}

	minBr := 30.0
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
