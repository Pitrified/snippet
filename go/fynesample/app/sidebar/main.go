package main

import (
	"fmt"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"
)

// --------------------------------------------------------------------------------
//  SIDEBAR
// --------------------------------------------------------------------------------

type mySidebar struct {
	title *widget.Label
}

func newSidebar() *mySidebar {
	return &mySidebar{}
}

func (s *mySidebar) buildSidebar() *fyne.Container {
	s.title = widget.NewLabel("The title")

	return container.NewVBox(s.title)
}

// --------------------------------------------------------------------------------
//  APPLICATION
// --------------------------------------------------------------------------------

type myApp struct {
	fyneApp fyne.App
	mainWin fyne.Window

	sidebar *mySidebar
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

	label1 := widget.NewLabel("Hello there")
	label2 := widget.NewLabel("(right aligned)")
	contentTitle := container.New(layout.NewHBoxLayout(), label1, layout.NewSpacer(), label2)

	a.sidebar = newSidebar()
	contSidebar := a.sidebar.buildSidebar()

	// borderCont := container.New(layout.NewBorderLayout(contentTitle, contentInput, nil, nil),
	// 	contentTitle, contentInput, contentImg)
	borderCont := container.New(
		layout.NewBorderLayout(contentTitle, nil, nil, contSidebar),
		contentTitle, contSidebar,
	)

	a.mainWin.SetContent(borderCont)
}

func (a *myApp) typedKey(ev *fyne.KeyEvent) {
	fmt.Printf("typedKey  = %+v %T\n", ev, ev)
	switch ev.Name {
	case fyne.KeyEscape, fyne.KeyQ:
		a.fyneApp.Quit()
	default:
	}
}

func (a *myApp) runApp() {
	a.mainWin.Resize(fyne.NewSize(1200, 1200))
	a.mainWin.Show()
	a.fyneApp.Run()
}

// --------------------------------------------------------------------------------
//  MAIN
// --------------------------------------------------------------------------------

func main() {
	fmt.Println("vim-go")

	theApp := newApp()
	theApp.buildUI()
	theApp.runApp()
}
