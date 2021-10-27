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

// Clicked one of the rotate bank buttons
func (s *mySidebar) rotBankCallback(id float64) {
	fmt.Printf("Pressed button %+v\n", id)
	oldValue, err := s.rotValBind.Get()
	if err != nil {
		return
	}
	s.rotValBind.Set(oldValue + float64(id))
}

// Clicked the val set button
func (s *mySidebar) rotValCallback() {
	val, err := s.rotValBind.Get()
	if err != nil {
		return
	}
	// the value in rotValBind is already correct: now tell this to the turtle
	fmt.Printf("Set the rot value to %.3f\n", val)
}

// Press enter on the val entry
func (s *mySidebar) rotValSubmitted(_ string) {
	s.rotValCallback()
}

// Clicked delta button
func (s *mySidebar) rotDeltaCallback() {
	// string in the entry
	str := s.rotDeltaEntry.Text
	// convert it to float
	entryVal, err := strconv.ParseFloat(str, 64)
	if err != nil {
		fmt.Printf("Failed to parse str = %q\n", str)
		return
	}
	fmt.Printf("Rotated the rot value by %.3f\n", entryVal)
	// current value of rotation
	curVal, err := s.rotValBind.Get()
	if err != nil {
		return
	}
	s.rotValBind.Set(entryVal + curVal)
}

// Press enter on the delta entry
func (s *mySidebar) rotDeltaSubmitted(_ string) {
	s.rotDeltaCallback()
}

func (s *mySidebar) buildSidebar() *fyne.Container {
	s.title = widget.NewLabelWithStyle(
		"The title",
		fyne.TextAlignCenter,
		fyne.TextStyle{Bold: true},
	)

	// ----- Bank of buttons -----

	rotVal := map[int]float64{0: -10, 1: -1, 2: -0.1, 3: 0.1, 4: 1, 5: 10}
	s.rotBank = make([]*widget.Button, 6)
	for i := 0; i < len(s.rotBank); i++ {
		c := rotVal[i]
		s.rotBank[i] = widget.NewButton(
			fmt.Sprintf("%+v", c),
			func() { s.rotBankCallback(c) },
		)
	}
	contBank := container.NewGridWithColumns(
		6,
		s.rotBank[0], s.rotBank[1], s.rotBank[2], s.rotBank[3], s.rotBank[4], s.rotBank[5],
	)

	// ----- Entry to rotate by this value -----

	deltaLabel := widget.NewLabel("Rotate by:")
	s.rotDeltaEntry = widget.NewEntry()
	s.rotDeltaEntry.Text = "0.0"
	s.rotDeltaEntry.OnSubmitted = s.rotDeltaSubmitted
	s.rotDeltaSet = widget.NewButton("Rotate", s.rotDeltaCallback)
	contDelta := container.NewBorder(nil, nil, deltaLabel, s.rotDeltaSet, s.rotDeltaEntry)

	// ----- Entry to set new value -----

	valLabel := widget.NewLabel("Current:")
	s.rotValBind = binding.BindFloat(&s.rotValF64)
	s.rotValEntry = widget.NewEntryWithData(binding.FloatToString(s.rotValBind))
	s.rotValEntry.OnSubmitted = s.rotValSubmitted
	s.rotValSet = widget.NewButton("Set", s.rotValCallback)
	contVal := container.NewBorder(nil, nil, valLabel, s.rotValSet, s.rotValEntry)

	// ----- Card with rotate widgets -----

	contCard := container.NewVBox(contBank, contDelta, contVal)
	s.rotate = widget.NewCard("Orientation", "", contCard)

	// ----- All the sidebar content -----

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
