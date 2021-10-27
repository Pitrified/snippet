package main

import (
	"fmt"

	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/data/binding"
	"fyne.io/fyne/v2/widget"
)

func main() {
	fmt.Println("vim-go")

	app := app.New()
	win := app.NewWindow("Bind test")

	f := 0.2
	data := binding.BindFloat(&f)
	label := widget.NewLabelWithData(binding.FloatToStringWithFormat(data, "Float value: %0.6f"))

	// with binding A the input is received
	// but if the content is 0._200000 (_ is the cursor) and the dot is removed
	// the content becomes 2_00000.000000
	// https://github.com/fyne-io/fyne/issues/1849
	// entry := widget.NewEntryWithData(binding.FloatToString(data))

	// with binding B no input is received
	// duh: https://pkg.go.dev/fmt
	// the 0 means 0 width, so it does not make sense
	// entry := widget.NewEntryWithData(binding.FloatToStringWithFormat(data, "%0.6f"))

	// with binding B+ the input is received
	entry := widget.NewEntryWithData(binding.FloatToStringWithFormat(data, "%10.6f"))

	// with binding C the input is received
	// entry := widget.NewEntryWithData(binding.FloatToStringWithFormat(data, "%.6f"))

	win.SetContent(container.NewGridWithColumns(2, label, entry))

	win.Show()
	app.Run()
}
