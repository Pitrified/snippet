package main

import (
	"fmt"
	"strconv"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/data/binding"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"
)

// --------------------------------------------------------------------------------
//  SIDEBAR
// --------------------------------------------------------------------------------

type mySidebar struct {
	a *myApp

	title *widget.Label

	rotate        *widget.Card
	rotBank       []*widget.Button
	rotValEntry   *widget.Entry
	rotValF64     float64
	rotValBind    binding.ExternalFloat
	rotValSet     *widget.Button
	rotDeltaEntry *widget.Entry
	rotDeltaSet   *widget.Button
}

func newSidebar(a *myApp) *mySidebar {
	return &mySidebar{a: a}
}

func (s *mySidebar) clickRotBank(id int) {
	fmt.Printf("Pressed button %+v\n", id)
	oldValue, err := s.rotValBind.Get()
	if err != nil {
		return
	}
	s.rotValBind.Set(oldValue + float64(id))
}

func (s *mySidebar) buildSidebar() *fyne.Container {
	s.title = widget.NewLabelWithStyle(
		"The title",
		fyne.TextAlignCenter,
		fyne.TextStyle{Bold: true},
	)

	// ----- Bank of buttons -----

	// TODO use a map to use already correct values rot[0]=-10
	s.rotBank = make([]*widget.Button, 6)
	for i := 0; i < len(s.rotBank); i++ {
		c := i
		s.rotBank[i] = widget.NewButton(
			fmt.Sprintf("B: %d", i),
			func() {
				s.clickRotBank(c)
			},
		)
	}
	contBank := container.NewHBox(
		s.rotBank[0],
		s.rotBank[1],
		s.rotBank[2],
		s.rotBank[3],
		s.rotBank[4],
		s.rotBank[5],
	)

	// ----- Entry to rotate by this value -----

	s.rotDeltaEntry = widget.NewEntry()
	s.rotDeltaEntry.PlaceHolder = "0.0"
	s.rotDeltaSet = widget.NewButton(
		"Rotate",
		func() {
			str := s.rotDeltaEntry.Text
			val, err := strconv.ParseFloat(str, 64)
			if err != nil {
				fmt.Printf("Failed to parse str = %q\n", str)
				return
			}
			fmt.Printf("Rotated the rot value by %.3f\n", val)
		},
	)
	contDelta := container.NewBorder(nil, nil, nil, s.rotDeltaSet, s.rotDeltaEntry)

	// ----- Entry to set new value -----

	s.rotValBind = binding.BindFloat(&s.rotValF64)
	s.rotValEntry = widget.NewEntryWithData(binding.FloatToString(s.rotValBind))
	s.rotValSet = widget.NewButton(
		"Set",
		func() {
			val, err := s.rotValBind.Get()
			if err != nil {
				return
			}
			fmt.Printf("Set the rot value to %.3f\n", val)
		},
	)
	contVal := container.NewBorder(nil, nil, nil, s.rotValSet, s.rotValEntry)

	// ----- Card with rotate widgets -----

	contCard := container.NewVBox(contBank, contDelta, contVal)

	s.rotate = widget.NewCard("Rotate", "", contCard)

	// vCont := container.NewVBox(s.rotate, contBank)
	vCont := container.NewVBox(s.title, s.rotate)
	return vCont
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

	a.sidebar = newSidebar(a)
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
