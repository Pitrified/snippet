package main

import (
	"blinker/cellfire"
	"fmt"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

// --------------------------------------------------------------------------------
//  APP
// --------------------------------------------------------------------------------

type myApp struct {
	fyneApp fyne.App
	mainWin fyne.Window
}

func newApp() *myApp {

	// create the app
	fyneApp := app.New()
	mainWin := fyneApp.NewWindow("Image test")
	theApp := &myApp{fyneApp: fyneApp, mainWin: mainWin}

	// add the link for typed runes
	theApp.mainWin.Canvas().SetOnTypedKey(theApp.typedKey)

	return theApp
}

func (a *myApp) buildUI() {
	borderCont := container.NewBorder(widget.NewLabel("Top"), widget.NewLabel("Bottom"), nil, nil)

	a.mainWin.SetContent(borderCont)
}

func (a *myApp) runApp() {
	a.mainWin.Resize(fyne.NewSize(900, 900))
	a.mainWin.Show()
	a.fyneApp.Run()
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
//  MAIN
// --------------------------------------------------------------------------------

func main() {
	fmt.Println("vim-go")

	cw, ch := 3, 3
	cellSize := float32(100)
	nF := 10
	w := cellfire.NewWorld(cw, ch, cellSize)
	w.HatchFireflies(nF)
	fmt.Printf("%+v\n", w)

	theApp := newApp()
	theApp.buildUI()
	theApp.runApp()
}
