package main

import (
	"fmt"
	"image/color"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
)

type mySidebar struct {
	a *myApp

	moveCard   *widget.Card
	moveBank   []*widget.Button
	moveSetBtn *widget.Button
	moveSetX   *widget.Entry
	moveSetY   *widget.Entry

	rotCard   *widget.Card
	rotBank   []*widget.Button
	rotSetBtn *widget.Button
	rotSet    *widget.Entry

	penCard     *widget.Card
	penCheck    *widget.Check
	penPicker   *dialog.ColorPickerDialog
	penPickShow *widget.Button
	penCurrent  *canvas.Rectangle
	penSizeLab  *widget.Label
	penSizeSli  *widget.Slider

	resCard *widget.Card

	specCard *widget.Card

	saveCard   *widget.Card
	saveSet    *widget.Entry
	saveSetBtn *widget.Button
}

func newSidebar(a *myApp) *mySidebar {
	return &mySidebar{a: a}
}

// --------------------------------------------------------------------------------
//  Build the sidebar
// --------------------------------------------------------------------------------

// Build the sidebar.
func (s *mySidebar) buildSidebar() *fyne.Container {
	return container.NewVBox(
		s.buildMove(),
		s.buildRotate(),
		s.buildPen(),
		s.buildReset(),
		s.buildSpec(),
		s.buildSave(),
	)
}

// --------------------------------------------------------------------------------
//  Build the move card
// --------------------------------------------------------------------------------

// Build the move card.
func (s *mySidebar) buildMove() *widget.Card {

	// buttons to control the movement
	moveVal := map[int]float64{0: -10, 1: -1, 2: -0.1, 3: 0.1, 4: 1, 5: 10}
	s.moveBank = make([]*widget.Button, 6)
	for i := 0; i < len(s.moveBank); i++ {
		c := moveVal[i]
		s.moveBank[i] = widget.NewButton(
			fmt.Sprintf("%+v", c),
			func() { s.moveBankCB(c) },
		)
	}
	contMoveBank := container.NewGridWithColumns(
		6,
		s.moveBank[0], s.moveBank[1], s.moveBank[2], s.moveBank[3], s.moveBank[4], s.moveBank[5],
	)

	// ##### entries + button to set position #####

	s.moveSetBtn = widget.NewButton("Set", s.moveSetBtnCB)
	// Entry x
	s.moveSetX = widget.NewEntry()
	s.moveSetX.Text = "0.000"
	s.moveSetX.Wrapping = fyne.TextWrapOff
	s.moveSetX.OnSubmitted = s.moveSetSubmitted
	// Entry y
	s.moveSetY = widget.NewEntry()
	s.moveSetY.Text = "0.000"
	s.moveSetY.Wrapping = fyne.TextWrapOff
	s.moveSetY.OnSubmitted = s.moveSetSubmitted
	// Labels
	labMoveX := widget.NewLabel("X:")
	labMoveY := widget.NewLabel("Y:")
	// Pair label and entry
	elMoveX := container.NewBorder(nil, nil, labMoveX, nil, s.moveSetX)
	elMoveY := container.NewBorder(nil, nil, labMoveY, nil, s.moveSetY)
	// Pair the EL
	elMoveXY := container.NewGridWithColumns(2, elMoveX, elMoveY)
	// Pair the ELpair and the button
	contMoveSet := container.NewBorder(nil, nil, nil, s.moveSetBtn, elMoveXY)

	// build the card
	contCard := container.NewVBox(contMoveBank, contMoveSet)
	s.moveCard = widget.NewCard("Move", "Position:", contCard)
	return s.moveCard
}

// ##### Reactions to user input #####

// Clicked one of the move bank buttons
func (s *mySidebar) moveBankCB(d float64) {
	fmt.Printf("SIDE: moveBankCB d = %+v\n", d)
	s.a.c.move(d)
}

// Clicked button set position from entries.
func (s *mySidebar) moveSetBtnCB() {
	// try to parse the text
	x, errX := entry2F64(s.moveSetX)
	y, errY := entry2F64(s.moveSetY)
	if errX != nil || errY != nil {
		return
	}
	fmt.Printf("SIDE: moveSetBtnCB x, y = %+v, %+v\n", x, y)

	// tell the controller that we want to teleport there
	s.a.c.jump(x, y)
}

// Press enter on either set pos entry.
func (s *mySidebar) moveSetSubmitted(_ string) {
	s.moveSetBtnCB()
}

// ##### Update the widgets #####

// The position changed.
func (s *mySidebar) updatePos(x, y float64) {
	fmt.Printf("SIDE: updatePos x, y = %+v, %+v\n", x, y)
	// in the label, show short number if it grows large
	s.moveCard.SetSubTitle(fmt.Sprintf("Position: (%.5g, %.5g)", x, y))
	// in the entries, always show all digits
	s.moveSetX.SetText(FormatFloat(x, 3))
	s.moveSetY.SetText(FormatFloat(y, 3))
}

// --------------------------------------------------------------------------------
//  Build the rotate card
// --------------------------------------------------------------------------------

func (s *mySidebar) buildRotate() *widget.Card {

	// buttons to control the rotation
	rotVal := map[int]float64{0: -10, 1: -1, 2: -0.1, 3: 0.1, 4: 1, 5: 10}
	s.rotBank = make([]*widget.Button, 6)
	for i := 0; i < len(s.rotBank); i++ {
		c := rotVal[i]
		s.rotBank[i] = widget.NewButton(
			fmt.Sprintf("%+v", c),
			func() { s.rotBankCB(c) },
		)
	}
	contRotBank := container.NewGridWithColumns(
		6,
		s.rotBank[0], s.rotBank[1], s.rotBank[2], s.rotBank[3], s.rotBank[4], s.rotBank[5],
	)

	// entries + button to set the rotation
	s.rotSetBtn = widget.NewButton("Set", s.rotSetBtnCB)
	s.rotSet = widget.NewEntry()
	s.rotSet.Text = "0.000"
	s.rotSet.Wrapping = fyne.TextWrapOff
	s.rotSet.OnSubmitted = s.rotSetSubmitted
	labRot := widget.NewLabel("Deg:")
	contRotSet := container.NewBorder(nil, nil, labRot, s.rotSetBtn, s.rotSet)

	// card content
	contCard := container.NewVBox(contRotBank, contRotSet)
	s.rotCard = widget.NewCard("Rotate", "Orientation:", contCard)
	return s.rotCard
}

// ##### Reactions to user input #####

// Clicked one of the rotate bank buttons
func (s *mySidebar) rotBankCB(d float64) {
	fmt.Printf("SIDE: rotBankCB d = %+v\n", d)
	s.a.c.rotate(d)
}

// Clicked button set orientation from entry.
func (s *mySidebar) rotSetBtnCB() {
	// try to parse the text
	o, err := entry2F64(s.rotSet)
	if err != nil {
		return
	}
	fmt.Printf("SIDE: rotSetBtnCB o = %+v\n", o)

	s.a.c.setOri(o)
}

// Press enter on set orientation entry.
func (s *mySidebar) rotSetSubmitted(_ string) {
	s.rotSetBtnCB()
}

// ##### Update the widgets #####

// The orientation changed.
func (s *mySidebar) updateOri(o float64) {
	fmt.Printf("SIDE: updateOri o = %+v\n", o)
	// in the label, show short number if it grows large
	s.rotCard.SetSubTitle(fmt.Sprintf("Current orientation: %.5g", o))
	// in the entries, always show all digits
	s.rotSet.SetText(FormatFloat(o, 3))
}

// --------------------------------------------------------------------------------
//  Build the pen card
// --------------------------------------------------------------------------------

func (s *mySidebar) buildPen() *widget.Card {

	// toggle the pen
	s.penCheck = widget.NewCheck("Draw", s.penCheckCB)
	s.penCheck.Checked = true

	// dialog shown when clicking the button
	s.penPickShow = widget.NewButton("Change", s.penPickerShowCB)
	s.penPicker = dialog.NewColorPicker("Pick a color", "Pen color",
		s.penPickerCB, s.a.mainWin)
	s.penPicker.Advanced = true

	// current color
	s.penCurrent = canvas.NewRectangle(color.RGBA{})
	size := 2 * theme.IconInlineSize()
	s.penCurrent.SetMinSize(fyne.NewSize(size, size))

	// first row of widgets
	contRow1 := container.NewHBox(
		s.penCheck,
		layout.NewSpacer(),
		s.penCurrent, s.penPickShow)

	// second row of widgets
	s.penSizeLab = widget.NewLabel("Size:")
	s.penSizeSli = widget.NewSlider(1, 30)
	s.penSizeSli.Step = 1
	s.penSizeSli.OnChanged = s.penSizeSliCB
	contRow2 := container.NewBorder(nil, nil, s.penSizeLab, nil, s.penSizeSli)

	contCard := container.NewVBox(contRow1, contRow2)
	s.penCard = widget.NewCard("Pen", "", contCard)
	return s.penCard
}

// ##### Reactions to user input #####

func (s *mySidebar) penPickerCB(c color.Color) {
	fmt.Printf("SIDE: penPickerCB c = %+v\n", c)
	s.a.c.setPenColor(c)
}

func (s *mySidebar) penPickerShowCB() {
	s.penPicker.Show()
}

func (s *mySidebar) penCheckCB(b bool) {
	fmt.Printf("SIDE: penCheckCB b = %+v\n", b)
	s.a.c.setPenState(b)
}

func (s *mySidebar) penSizeSliCB(f float64) {
	fmt.Printf("SIDE: penSizeSliCB f = %+v\n", f)
	s.a.c.setPenSize(f)
}

// ##### Update the widgets #####

func (s *mySidebar) updatePenColor(c color.Color) {
	s.penCurrent.FillColor = c
	canvas.Refresh(s.penCurrent)
}

func (s *mySidebar) updatePenSize(i int) {
	s.penSizeLab.SetText(fmt.Sprintf("Size: %d", i))
	s.penSizeSli.SetValue(float64(i))
}

// --------------------------------------------------------------------------------
//  Build the special card
// --------------------------------------------------------------------------------

// Hilbert.
func (s *mySidebar) buildSpec() *widget.Card {
	s.specCard = widget.NewCard("Special", "", nil)
	return s.specCard
}

// --------------------------------------------------------------------------------
//  Build the reset card
// --------------------------------------------------------------------------------

func (s *mySidebar) buildReset() *widget.Card {
	s.resCard = widget.NewCard("Reset", "", nil)
	return s.resCard
}

// --------------------------------------------------------------------------------
//  Build the save card
// --------------------------------------------------------------------------------

func (s *mySidebar) buildSave() *widget.Card {

	s.saveSetBtn = widget.NewButton("Save", s.saveSetBtnCB)
	s.saveSet = widget.NewEntry()
	s.saveSet.Text = "out.png"
	s.saveSet.Wrapping = fyne.TextWrapOff
	s.saveSet.OnSubmitted = s.saveSetSubmitted
	saveLab := widget.NewLabel("To:")

	contSaveSet := container.NewBorder(nil, nil, saveLab, s.saveSetBtn, s.saveSet)
	s.saveCard = widget.NewCard("Save", "", contSaveSet)
	return s.saveCard
}

// ##### Reactions to user input #####

// Clicked button set orientation from entry.
func (s *mySidebar) saveSetBtnCB() {
	p := s.saveSet.Text
	fmt.Printf("SIDE: s.saveSet.Text = %+v\n", p)
	s.a.c.save(p)
}

// Press enter on set orientation entry.
func (s *mySidebar) saveSetSubmitted(_ string) {
	s.saveSetBtnCB()
}
