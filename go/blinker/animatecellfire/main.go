package main

import (
	"blinker/cellfire"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"sync"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

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
}

// Create a new app.
func newApp() *myApp {

	// create the app
	fyneApp := app.New()
	mainWin := fyneApp.NewWindow("Image test")
	a := &myApp{fyneApp: fyneApp, mainWin: mainWin}

	// add the link for typed runes
	a.mainWin.Canvas().SetOnTypedKey(a.typedKey)

	// create the world to simulate
	a.wCellW, a.wCellH = 3, 3
	a.wCellSize = 100
	a.w = cellfire.NewWorld(a.wCellW, a.wCellH, float32(a.wCellSize))
	nF := 10
	a.w.HatchFireflies(nF)
	// fmt.Printf("%+v\n", w)

	// size of the image to render the world in
	// MAYBE needs a -1 on the right/top border
	a.wSize = image.Rect(0, 0, a.wCellW*a.wCellSize, a.wCellH*a.wCellSize)

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

	borderCont := container.NewBorder(
		widget.NewLabel("Top"),
		widget.NewLabel("Bottom"),
		nil, nil,
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
		tickRender := time.NewTicker(time.Second / 2)

		// for { select { case <-tickRender.C: } }
		for range tickRender.C {
			a.renderWorld()
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
	fmt.Printf("a.wSize = %+v\n", a.wSize)

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

	left := c.Cx * a.wCellSize
	bottom := c.Cy * a.wCellSize
	col := uint8(10*c.Cx + 30*c.Cy)

	for i := 0; i < a.wCellSize; i++ {
		for ii := 0; ii < a.wCellSize; ii++ {
			m.Set(left+i, bottom+ii, color.RGBA{col, col, col, 255})
		}
	}

	a.wCellWG.Done()
}

// --------------------------------------------------------------------------------
//  MAIN
// --------------------------------------------------------------------------------

func main() {
	fmt.Println("vim-go")

	theApp := newApp()
	theApp.buildUI()
	theApp.animate()
	theApp.runApp()
}
