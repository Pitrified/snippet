package main

import (
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/widget"
)

type WideEntry struct {
	widget.Entry

	minSize fyne.Size
}

func (e *WideEntry) MinSize() fyne.Size {
	s := e.Entry.MinSize()
	w := MaxFloat32(s.Width, e.minSize.Width)
	h := MaxFloat32(s.Height, e.minSize.Height)
	return fyne.NewSize(w, h)
}

func NewWideEntry(s fyne.Size) *WideEntry {
	e := &WideEntry{minSize: s}
	e.ExtendBaseWidget(e)
	return e
}
