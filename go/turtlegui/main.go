package main

import (
	"image/color"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
)

func main() {
	app := app.New()

	win := app.NewWindow("Hello")

	// win.SetContent(widget.NewLabel("Hello Fyne!"))

	myCanvas := win.Canvas()

	text := canvas.NewText("Text", color.White)
	text.TextStyle.Bold = true
	myCanvas.SetContent(text)

	// rect := canvas.NewRectangle(color.White)
	// win.SetContent(rect)

	// line := canvas.NewLine(color.White)
	// line.StrokeWidth = 5
	// win.SetContent(line)

	win.Resize(fyne.NewSize(100, 100))
	win.Show()
	app.Run()
}
