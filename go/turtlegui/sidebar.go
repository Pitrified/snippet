package main

import (
	"fmt"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

type mySidebar struct {
	a *myApp

	moveCard   *widget.Card
	moveBank   []*widget.Button
	moveLabel  *widget.Label
	moveSetBtn *widget.Button
	moveSetX   *widget.Entry
	moveSetY   *widget.Entry

	rotCard *widget.Card

	penCard *widget.Card
}

func newSidebar(a *myApp) *mySidebar {
	return &mySidebar{a: a}
}

// --------------------------------------------------------------------------------
//  Build the sidebar
// --------------------------------------------------------------------------------

// Build the sidebar.
func (s *mySidebar) buildSidebar() *fyne.Container {

	s.buildMove()
	s.buildRotate()
	s.buildPen()

	// ----- All the sidebar content -----

	vCont := container.NewVBox(s.moveCard, s.rotCard, s.penCard)
	// vCont := container.NewVBox(s.title, s.moveCard)
	return vCont
}

// --------------------------------------------------------------------------------
//  Build the move card
// --------------------------------------------------------------------------------

// Build the move card.
func (s *mySidebar) buildMove() {

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

	// label with the current position
	s.moveLabel = widget.NewLabel("Current pos:")

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
	contCard := container.NewVBox(contMoveBank, s.moveLabel, contMoveSet)
	s.moveCard = widget.NewCard("Move", "", contCard)
}

// ##### Reactions to user input #####

// Clicked one of the rotate bank buttons
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

// Press enter on either set entry.
func (s *mySidebar) moveSetSubmitted(_ string) {
	s.moveSetBtnCB()
}

// ##### Update the widgets #####

// The position changed.
func (s *mySidebar) updatePos(x, y float64) {
	fmt.Printf("SIDE: updatePos x, y = %+v, %+v\n", x, y)
	// in the label, show short number if it grows large
	s.moveLabel.SetText(fmt.Sprintf("Current pos: (%.5g, %.5g)", x, y))
	// in the entries, always show all digits
	s.moveSetX.SetText(FormatFloat(x, 3))
	s.moveSetY.SetText(FormatFloat(y, 3))
}

// --------------------------------------------------------------------------------
//  Build the rotate card
// --------------------------------------------------------------------------------

func (s *mySidebar) buildRotate() {
	s.rotCard = widget.NewCard("Rotate", "", nil)
}

// --------------------------------------------------------------------------------
//  Build the pen card
// --------------------------------------------------------------------------------

func (s *mySidebar) buildPen() {
	s.penCard = widget.NewCard("Pen", "", nil)
}
