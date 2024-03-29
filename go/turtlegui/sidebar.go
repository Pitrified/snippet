package main

import (
	"fmt"
	"image/color"
	"math"
	"net/url"
	"os"

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

	moveCard    *widget.Card
	moveBank    []*widget.Button
	moveSetBtn  *widget.Button
	moveSetX    *WideEntry
	moveSetY    *widget.Entry
	moveCustBtn *widget.Button
	moveCustEnt *widget.Entry

	rotCard    *widget.Card
	rotBank    []*widget.Button
	rotSetBtn  *widget.Button
	rotSet     *widget.Entry
	rotCustBtn *widget.Button
	rotCustEnt *widget.Entry

	penCard     *widget.Card
	penCheck    *widget.Check
	penPicker   *dialog.ColorPickerDialog
	penPickShow *widget.Button
	penCurrent  *canvas.Rectangle
	penSizeLab  *widget.Label
	penSizeSli  *widget.Slider

	resCard     *widget.Card
	resReset    *widget.Button
	resResetW   *WideEntry
	resResetH   *widget.Entry
	resPicker   *dialog.ColorPickerDialog
	resPickShow *widget.Button
	resCurrent  *canvas.Rectangle

	specCard   *widget.Card
	specNamesM map[string]string
	specNamesS []string
	specSel    *widget.Select
	specGo     *widget.Button
	specLevel  *widget.Entry
	specLenght *widget.Entry

	saveCard        *widget.Card
	saveSet         *widget.Entry
	saveSetBtn      *widget.Button
	saveConfirmPath string

	miscCard   *widget.Card
	miscCredit *widget.Button
	miscHelp   *widget.Button
	miscFull   *widget.Button
}

func newSidebar(a *myApp) *mySidebar {
	return &mySidebar{a: a}
}

// --------------------------------------------------------------------------------
//  Build the sidebar
// --------------------------------------------------------------------------------

// Build the sidebar.
func (s *mySidebar) buildSidebar() *container.Scroll {
	return container.NewVScroll(
		container.NewVBox(
			s.buildMove(),
			s.buildRotate(),
			s.buildPen(),
			s.buildReset(),
			s.buildSpec(),
			s.buildSave(),
			s.buildMisc(),
		),
	)
}

// --------------------------------------------------------------------------------
//  Build the move card
// --------------------------------------------------------------------------------

// Build the move card.
func (s *mySidebar) buildMove() *widget.Card {

	// buttons to control the movement
	moveVal := map[int]float64{0: -50, 1: -10, 2: 10, 3: 50}
	s.moveBank = make([]*widget.Button, 4)
	for i := 0; i < len(s.moveBank); i++ {
		c := moveVal[i]
		s.moveBank[i] = widget.NewButton(
			fmt.Sprintf("%+v", c),
			func() { s.moveBankCB(c) },
		)
	}
	contMoveBank := container.NewGridWithColumns(
		4,
		s.moveBank[0], s.moveBank[1], s.moveBank[2], s.moveBank[3],
	)
	labBank := widget.NewLabel("Move by:")
	contBank := container.NewBorder(nil, nil, labBank, nil, contMoveBank)

	// ##### entries + button to move by custom amount #####

	s.moveCustBtn = widget.NewButton("Move", s.moveCustBtnCB)
	s.moveCustEnt = widget.NewEntry()
	s.moveCustEnt.Text = "20"
	s.moveCustEnt.OnSubmitted = s.moveCustSubmitted
	labCust := widget.NewLabel("Move by:")
	contCust := container.NewBorder(nil, nil, labCust, s.moveCustBtn, s.moveCustEnt)

	// ##### entries + button to set position #####

	s.moveSetBtn = widget.NewButton("Set", s.moveSetBtnCB)
	// Entry X, at least wide 4*IconInlineSize
	s.moveSetX = NewWideEntry(fyne.NewSize(4*theme.IconInlineSize(), 0))
	s.moveSetX.Text = "0.000"
	s.moveSetX.OnSubmitted = s.moveSetSubmitted
	// Entry Y, the width is set equal to X by the grid layout
	s.moveSetY = widget.NewEntry()
	s.moveSetY.Text = "0.000"
	s.moveSetY.OnSubmitted = s.moveSetSubmitted
	// Labels
	labMoveX := widget.NewLabel("X:")
	labMoveY := widget.NewLabel("Y:")
	// Pair label and entry
	elMoveX := container.NewBorder(nil, nil, labMoveX, nil, s.moveSetX)
	elMoveY := container.NewBorder(nil, nil, labMoveY, nil, s.moveSetY)
	// Pair the EL
	elMoveXY := container.NewGridWithColumns(2, elMoveX, elMoveY)
	// Pair the ELpair and the button and the label
	labPos := widget.NewLabel("Pos:")
	contMoveSet := container.NewBorder(nil, nil, labPos, s.moveSetBtn, elMoveXY)

	// build the card
	contCard := container.NewVBox(contMoveSet, contBank, contCust)
	s.moveCard = widget.NewCard("Move", "", contCard)
	return s.moveCard
}

// ##### Reactions to user input #####

// Clicked one of the move bank buttons
func (s *mySidebar) moveBankCB(d float64) {
	s.a.c.move(d)
}

// Clicked button set position from entries.
func (s *mySidebar) moveSetBtnCB() {
	// try to parse the text
	x, errX := entry2F64(&s.moveSetX.Entry)
	y, errY := entry2F64(s.moveSetY)
	if errX != nil || errY != nil {
		return
	}
	// tell the controller that we want to teleport there
	s.a.c.jump(x, y)
}

// Press enter on either set pos entry.
func (s *mySidebar) moveSetSubmitted(_ string) {
	s.moveSetBtnCB()
}

// Clicked button move custom amount.
func (s *mySidebar) moveCustBtnCB() {
	d, err := entry2F64(s.moveCustEnt)
	if err != nil {
		return
	}
	s.a.c.move(d)
}

// Press enter on move custom amount entry.
func (s *mySidebar) moveCustSubmitted(_ string) {
	s.moveCustBtnCB()
}

// ##### Update the widgets #####

// The position changed.
func (s *mySidebar) updatePos(x, y float64) {
	// in the label, show short number if it grows large
	// s.moveCard.SetSubTitle(fmt.Sprintf("Position: (%.5g, %.5g)", x, y))
	// in the entries, always show all digits
	// s.moveSetX.SetText(FormatFloat(x, 3))
	// s.moveSetY.SetText(FormatFloat(y, 3))
	// yeah no, show only 5 characters, more than enough
	s.moveSetX.SetText(fmt.Sprintf("%.5g", x))
	s.moveSetY.SetText(fmt.Sprintf("%.5g", y))
}

// --------------------------------------------------------------------------------
//  Build the rotate card
// --------------------------------------------------------------------------------

func (s *mySidebar) buildRotate() *widget.Card {

	// buttons to control the rotation
	rotVal := map[int]float64{0: -10, 1: -1, 2: 1, 3: 10}
	s.rotBank = make([]*widget.Button, 4)
	for i := 0; i < len(s.rotBank); i++ {
		c := rotVal[i]
		s.rotBank[i] = widget.NewButton(
			fmt.Sprintf("%+v", c),
			func() { s.rotBankCB(c) },
		)
	}
	contRotBank := container.NewGridWithColumns(
		4,
		s.rotBank[0], s.rotBank[1], s.rotBank[2], s.rotBank[3],
	)
	labBank := widget.NewLabel("Rotate by:")
	contBank := container.NewBorder(nil, nil, labBank, nil, contRotBank)

	// ##### entries + button to rotate by custom amount #####

	s.rotCustBtn = widget.NewButton("Rotate", s.rotCustBtnCB)
	s.rotCustEnt = widget.NewEntry()
	s.rotCustEnt.Text = "20"
	s.rotCustEnt.OnSubmitted = s.rotCustSubmitted
	labCust := widget.NewLabel("Rotate by:")
	contCust := container.NewBorder(nil, nil, labCust, s.rotCustBtn, s.rotCustEnt)

	// entries + button to set the rotation
	s.rotSetBtn = widget.NewButton("Set", s.rotSetBtnCB)
	s.rotSet = widget.NewEntry()
	s.rotSet.Text = "0.000"
	s.rotSet.OnSubmitted = s.rotSetSubmitted
	labRot := widget.NewLabel("Deg:")
	contRotSet := container.NewBorder(nil, nil, labRot, s.rotSetBtn, s.rotSet)

	// card content
	contCard := container.NewVBox(contRotSet, contBank, contCust)
	s.rotCard = widget.NewCard("Rotate", "", contCard)
	return s.rotCard
}

// ##### Reactions to user input #####

// Clicked one of the rotate bank buttons
func (s *mySidebar) rotBankCB(d float64) {
	s.a.c.rotate(d)
}

// Clicked button set orientation from entry.
func (s *mySidebar) rotSetBtnCB() {
	o, err := entry2F64(s.rotSet)
	if err != nil {
		return
	}
	s.a.c.setOri(o)
}

// Press enter on set orientation entry.
func (s *mySidebar) rotSetSubmitted(_ string) {
	s.rotSetBtnCB()
}

// Clicked button rotate custom amount.
func (s *mySidebar) rotCustBtnCB() {
	d, err := entry2F64(s.rotCustEnt)
	if err != nil {
		return
	}
	s.a.c.rotate(d)
}

// Press enter on rotate custom amount entry.
func (s *mySidebar) rotCustSubmitted(_ string) {
	s.rotCustBtnCB()
}

// ##### Update the widgets #####

// The orientation changed.
func (s *mySidebar) updateOri(o float64) {
	// in the label, show short number if it grows large
	// s.rotCard.SetSubTitle(fmt.Sprintf("Current orientation: %.5g°", o))
	// in the entries, always show all digits
	s.rotSet.SetText(FormatFloat(math.Mod(o, 360), 3))
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
	s.a.c.setPenColor(c)
}

func (s *mySidebar) penPickerShowCB() {
	s.penPicker.Show()
}

func (s *mySidebar) penCheckCB(b bool) {
	s.a.c.setPenState(b)
}

func (s *mySidebar) penSizeSliCB(f float64) {
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

func (s *mySidebar) updatePenState(b bool) {
	s.penCheck.SetChecked(b)
}

// --------------------------------------------------------------------------------
//  Build the special card
// --------------------------------------------------------------------------------

// Hilbert.
func (s *mySidebar) buildSpec() *widget.Card {

	// map from visualized names to labels
	// so if we change the visualized one, there is no need to change other code
	s.specNamesM = map[string]string{
		"Hilbert":              "hilbert",
		"Dragon":               "dragon",
		"Sierpinski Triangle":  "sierpTri",
		"Sierpinski Arrowhead": "sierpArrow",
	}
	// copy the keys to a slice
	s.specNamesS = make([]string, len(s.specNamesM))
	i := 0
	for k := range s.specNamesM {
		s.specNamesS[i] = k
		i++
	}
	// no-op on selection
	s.specSel = widget.NewSelect(s.specNamesS, func(_ string) {})
	s.specSel.Selected = s.specNamesS[0]
	s.specGo = widget.NewButton("Draw", s.specGoCB)
	selLabel := widget.NewLabel("Fractal:")
	contSel := container.NewBorder(nil, nil, selLabel, s.specGo,
		s.specSel)

	// recursion level
	s.specLevel = widget.NewEntry()
	s.specLevel.Text = "6"
	s.specLenght = widget.NewEntry()
	s.specLenght.Text = "20"

	labLevel := widget.NewLabel("Recursion level:")
	labLenght := widget.NewLabel("Segment lenght:")
	// Pair label and entry
	// elLevel := container.NewBorder(nil, nil, labLevel, nil, s.specLevel)
	// elLenght := container.NewBorder(nil, nil, labLenght, nil, s.specLenght)
	// // Pair the EL
	// elLL := container.NewGridWithColumns(2, elLevel, elLenght)
	elLL := container.NewHBox(labLevel, s.specLevel,
		layout.NewSpacer(),
		labLenght, s.specLenght)

	contCard := container.NewVBox(contSel, elLL)
	s.specCard = widget.NewCard("Special", "", contCard)
	return s.specCard
}

// Clicked button draw fractal.
func (s *mySidebar) specGoCB() {
	// data from the entries
	segLen, errS := entry2F64(s.specLenght)
	level, errL := entry2F64(s.specLevel)
	if errS != nil || errL != nil {
		return
	}
	levelI := int(math.Round(level))
	// data from the select
	visName := s.specSel.Selected
	tag := s.specNamesM[visName]

	// call the controller
	s.a.c.drawFractal(segLen, levelI, tag)
}

// --------------------------------------------------------------------------------
//  Build the reset card
// --------------------------------------------------------------------------------

func (s *mySidebar) buildReset() *widget.Card {

	// button to reset world
	s.resReset = widget.NewButton("Reset", s.resResetCB)
	// entries to set world size
	// Entry W, at least wide 4*IconInlineSize
	s.resResetW = NewWideEntry(fyne.NewSize(4*theme.IconInlineSize(), 0))
	s.resResetW.Text = "3840"
	s.resResetW.OnSubmitted = s.resResetSubmitted
	// Entry H, the width is set equal to W by the grid layout
	s.resResetH = widget.NewEntry()
	s.resResetH.Text = "2160"
	s.resResetH.OnSubmitted = s.resResetSubmitted
	// Labels
	labResetW := widget.NewLabel("W:")
	labResetH := widget.NewLabel("H:")
	// Pair label and entry
	elResetW := container.NewBorder(nil, nil, labResetW, nil, s.resResetW)
	elResetH := container.NewBorder(nil, nil, labResetH, nil, s.resResetH)
	// Pair the EL
	elResetWH := container.NewGridWithColumns(2, elResetW, elResetH)
	// Pair the ELpair and the button and the label
	labPos := widget.NewLabel("Size:")
	contReset := container.NewBorder(nil, nil, labPos, s.resReset, elResetWH)

	// color picker and button
	s.resPickShow = widget.NewButton("Change", s.resPickerShowCB)
	s.resPicker = dialog.NewColorPicker("Pick a color", "Pen color",
		s.resPickerCB, s.a.mainWin)
	s.resPicker.Advanced = true

	// current color
	s.resCurrent = canvas.NewRectangle(color.RGBA{10, 10, 10, 255})
	size := 2 * theme.IconInlineSize()
	s.resCurrent.SetMinSize(fyne.NewSize(size, size))

	contRow2 := container.NewHBox(
		widget.NewLabel("Background color:"),
		layout.NewSpacer(),
		s.resCurrent, s.resPickShow,
	)

	contCard := container.NewVBox(contReset, contRow2)
	s.resCard = widget.NewCard("Reset", "", contCard)
	return s.resCard
}

// Clicked button reset world.
func (s *mySidebar) resResetCB() {
	w, errW := entry2F64(&s.resResetW.Entry)
	h, errH := entry2F64(s.resResetH)
	if errW != nil || errH != nil {
		return
	}
	wi := int(math.Round(w))
	hi := int(math.Round(h))
	rc := s.resCurrent.FillColor
	s.a.c.reset(wi, hi, rc)
}

func (s *mySidebar) resResetSubmitted(_ string) {
	s.resResetCB()
}

// A color was selected from the color picker for the world background.
func (s *mySidebar) resPickerCB(c color.Color) {
	// We break the MVC pattern because this color is not part of the model,
	// but only something to reset the model with.
	s.resCurrent.FillColor = c
	canvas.Refresh(s.resCurrent)
}

// Show the color picker for the world background.
func (s *mySidebar) resPickerShowCB() {
	s.resPicker.Show()
}

// --------------------------------------------------------------------------------
//  Build the save card
// --------------------------------------------------------------------------------

func (s *mySidebar) buildSave() *widget.Card {

	s.saveSetBtn = widget.NewButton("Save", s.saveSetBtnCB)
	s.saveSet = widget.NewEntry()
	s.saveSet.Text = "out.png"
	s.saveSet.OnSubmitted = s.saveSetSubmitted
	saveLab := widget.NewLabel("To:")

	contSaveSet := container.NewBorder(nil, nil, saveLab, s.saveSetBtn, s.saveSet)
	s.saveCard = widget.NewCard("Save", "", contSaveSet)
	return s.saveCard
}

// ##### Reactions to user input #####

// Callback for the overwrite confirm dialog.
func (s *mySidebar) saveConfirmCB(overwrite bool) {
	p := s.saveConfirmPath
	if overwrite {
		s.a.c.save(p)
		fmt.Printf("overwrite %+v\n", p)
	}
}

// Clicked button save image.
func (s *mySidebar) saveSetBtnCB() {
	p := s.saveSet.Text
	// if the file exists, ask for overwrite
	if _, err := os.Stat(p); err == nil {
		s.saveConfirmPath = p
		cnf := dialog.NewConfirm(fmt.Sprintf("%s already exists", p),
			"Do you want to overwrite the file?",
			s.saveConfirmCB, s.a.mainWin)
		cnf.SetDismissText("No")
		cnf.SetConfirmText("Yes")
		cnf.Show()
	} else
	// save the file
	{
		s.a.c.save(p)
		fmt.Printf("saved %+v\n", p)
	}
}

// Press enter on save image file name entry.
func (s *mySidebar) saveSetSubmitted(_ string) {
	s.saveSetBtnCB()
}

// --------------------------------------------------------------------------------
//  Build the misc card
// --------------------------------------------------------------------------------

func (s *mySidebar) buildMisc() *widget.Card {
	s.miscCredit = widget.NewButton("Credits", s.miscCreditCB)
	s.miscHelp = widget.NewButton("Help", s.miscHelpCB)
	s.miscFull = widget.NewButton("Fullscreen", s.miscFullCB)
	// contCard := container.NewGridWithColumns(2, s.miscHelp, s.miscCredit)
	contCard := container.NewGridWithRows(1, s.miscHelp, s.miscFull, s.miscCredit)
	s.miscCard = widget.NewCard("Misc", "", contCard)
	return s.miscCard
}

// Clicked button show credits.
func (s *mySidebar) miscCreditCB() {
	w := CreditsWindow(fyne.CurrentApp(), fyne.NewSize(800, 400))
	w.Canvas().SetOnTypedKey(func(ev *fyne.KeyEvent) {
		if ev.Name == fyne.KeyEscape {
			w.Close()
		}
	})
	w.Show()
}

// Clicked button show help.
func (s *mySidebar) miscHelpCB() {
	w := s.a.fyneApp.NewWindow("Help")
	w.Canvas().SetOnTypedKey(func(ev *fyne.KeyEvent) {
		if ev.Name == fyne.KeyEscape {
			w.Close()
		}
	})
	explanation := widget.NewLabel(
		"The turtle movement and rotation amounts can be set using the 'Move by' and 'Rotate by' entries.")
	explanation.Wrapping = fyne.TextWrapWord
	urlRepo, _ := url.Parse("https://github.com/Pitrified/snippet/tree/master/go/turtlegui")
	titleAlign := fyne.TextAlignCenter
	titleStyle := fyne.TextStyle{Bold: true}
	cmdAlign := fyne.TextAlignTrailing
	cmdStyle := fyne.TextStyle{}
	descAlign := fyne.TextAlignLeading
	descStyle := fyne.TextStyle{}
	w.SetContent(container.NewVBox(
		widget.NewCard("Keyboard", "",
			container.NewVBox(
				widget.NewLabelWithStyle("Movement", titleAlign, titleStyle),
				container.NewHBox(
					container.NewVBox(
						widget.NewLabelWithStyle("Q", cmdAlign, cmdStyle),
						widget.NewLabelWithStyle("W", cmdAlign, cmdStyle),
						widget.NewLabelWithStyle("E", cmdAlign, cmdStyle),
						widget.NewLabelWithStyle("A", cmdAlign, cmdStyle),
						widget.NewLabelWithStyle("S", cmdAlign, cmdStyle),
						widget.NewLabelWithStyle("D", cmdAlign, cmdStyle),
					),
					container.NewVBox(
						widget.NewLabelWithStyle("Forward and left.", descAlign, descStyle),
						widget.NewLabelWithStyle("Forward.", descAlign, descStyle),
						widget.NewLabelWithStyle("Forward and right.", descAlign, descStyle),
						widget.NewLabelWithStyle("Left.", descAlign, descStyle),
						widget.NewLabelWithStyle("Backward.", descAlign, descStyle),
						widget.NewLabelWithStyle("Right.", descAlign, descStyle),
					),
				),
				explanation,
				widget.NewLabelWithStyle("Misc", titleAlign, titleStyle),
				container.NewHBox(
					container.NewVBox(
						widget.NewLabelWithStyle("H", cmdAlign, cmdStyle),
						widget.NewLabelWithStyle("ESC", cmdAlign, cmdStyle),
						widget.NewLabelWithStyle("F, F11", cmdAlign, cmdStyle),
					),
					container.NewVBox(
						widget.NewLabelWithStyle("Show this help.", descAlign, descStyle),
						widget.NewLabelWithStyle("Close the focused window.", descAlign, descStyle),
						widget.NewLabelWithStyle("Toggle fullscreen.", descAlign, descStyle),
					),
				),
			),
		),
		widget.NewCard("Credits", "",
			container.NewVBox(
				container.NewHBox(
					widget.NewLabel("Written by Pitrified."),
					widget.NewHyperlink("GitHub", urlRepo),
				),
				container.NewHBox(
					widget.NewLabel("Libraries used:"),
					widget.NewButton("Credits", s.miscCreditCB),
				),
			),
		),
		layout.NewSpacer(),
		widget.NewButton("Close", func() { w.Close() }),
	))
	w.Resize(fyne.NewSize(400, 150))
	w.Show()
}

// Clicked button toggle fullscreen.
func (s *mySidebar) miscFullCB() {
	s.a.toggleFullscreen()
}
