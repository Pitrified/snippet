package main

import (
	"fmt"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
)

type ScrollCustom struct {
	container.Scroll

	acc float64
}

func NewVScrollCustom(content fyne.CanvasObject, a float64) *ScrollCustom {
	s := &ScrollCustom{acc: a}
	s.Scroll = *container.NewVScroll(content)
	s.ExtendBaseWidget(s)
	return s
}

// Try to fix scroll amount
// https://github.com/fyne-io/fyne/issues/775
func (s *ScrollCustom) Scrolled(ev *fyne.ScrollEvent) {
	fmt.Printf("ev = %+v\n", ev)
	s.Scroll.Scrolled(ev)
	canvas.Refresh(s)
}
