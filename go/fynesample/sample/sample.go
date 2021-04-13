package main

import (
	"image/color"
	"log"
	"math/rand"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/data/binding"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
)

type SampleSlider struct {
	widget.Slider
}

func NewSampleSlider(min, max float64) *SampleSlider {
	sampleSlider := &SampleSlider{}
	sampleSlider.Min = min
	sampleSlider.Max = max
	sampleSlider.Step = 1
	sampleSlider.ExtendBaseWidget(sampleSlider)
	return sampleSlider
}

// While this works, you have a saner OnChanged func readily available.
func (ss *SampleSlider) Dragged(e *fyne.DragEvent) {
	log.Printf("Dragged %v %+v", ss.Value, e)
	ss.Slider.Dragged(e)
}

func (ss *SampleSlider) DragEnd() {
	log.Printf("DragEnd %v", ss.Value)
}

// Also saner because it is only called when the Value changes, not the position.
func sampleSliderOnChange(f float64) {
	log.Printf("sampleSliderOnChange %v", f)
}

// Create a custom layout to place the things exactly where you want.
// https://developer.fyne.io/tutorial/custom-layout
type wideHeader struct {
}

func (ws *wideHeader) MinSize(objects []fyne.CanvasObject) fyne.Size {
	w, h := float32(0), float32(0)
	for _, o := range objects {
		childSize := o.MinSize()
		w += childSize.Width
		if h < childSize.Height {
			h = childSize.Height
		}
	}
	return fyne.NewSize(w, h)
}

func (ws *wideHeader) Layout(objects []fyne.CanvasObject, containerSize fyne.Size) {
	leftMinSize := objects[0].MinSize()
	rightMinSize := objects[1].MinSize()
	leftSize := fyne.NewSize(containerSize.Width-rightMinSize.Width, leftMinSize.Height)
	pos := fyne.NewPos(0, 0)
	objects[0].Resize(leftSize)
	objects[0].Move(pos)
	pos = pos.Add(fyne.NewPos(leftSize.Width, 0))
	objects[1].Resize(rightMinSize)
	objects[1].Move(pos)
}

func main() {
	app := app.New()

	win := app.NewWindow("Hello")

	// win.SetContent(widget.NewLabel("Hello Fyne!"))

	// explicitly create a canvas and fill it with things
	// myCanvas := win.Canvas()
	// text := canvas.NewText("Text", color.White)
	// text.TextStyle.Bold = true
	// myCanvas.SetContent(text)

	// text := canvas.NewText("Text", color.White)
	// text.TextStyle.Bold = true
	// win.SetContent(text)

	// rect := canvas.NewRectangle(color.White)
	// win.SetContent(rect)

	// line := canvas.NewLine(color.White)
	// line.StrokeWidth = 5
	// win.SetContent(line)

	// https://developer.fyne.io/tour/canvas/image.html
	// A canvas.Image represents a scalable image resource in Fyne. It can be
	// loaded from a resource (as shown in the example), from an image file,
	// from a URI location containing an image, from an io.Reader, or from a Go
	// image.Image in memory.
	// The default image fill mode is canvas.ImageFillStretch which will cause
	// it to fill the space specified (through Resize() or layout).
	// Alternatively you could use canvas.ImageFillContain to ensure that the
	// aspect ratio is maintained and the image is within the bounds. Further
	// to this you can use canvas.ImageFillOriginal (as used in the example
	// here) which ensures that it will also have a minimum size equal to that
	// of the original image size.
	// Images can be bitmap based (like PNG and JPEG) or vector based (such as
	// SVG). Where possible we recommend scalable images as they will continue
	// to render well as sizes change. Be careful when using original image
	// sizes as they may not behave exactly as expected with different user
	// interface scales. As Fyne allows the entire user interface to scale a
	// 25px image file may not be the same height as a 25 height fyne object.

	image := canvas.NewImageFromResource(theme.FyneLogo())
	// image := canvas.NewImageFromURI(uri)
	// image := canvas.NewImageFromImage(src)
	// image := canvas.NewImageFromReader(reader, name)
	// image := canvas.NewImageFromFile(fileName)
	image.FillMode = canvas.ImageFillOriginal
	// win.SetContent(image)

	// https://developer.fyne.io/tour/canvas/raster.html
	// The canvas.Raster is like an image but draws exactly one spot for each
	// pixel on the screen. This means that as a user interface scales or the
	// image resizes more pixels will be requested to fill the space. To do
	// this we use a Generator function as illustrated in this example - it
	// will be used to return the colour of each pixel.
	// The generator functions can be pixel based (as in this example where we
	// generate a new random colour for each pixel) or based on full images.
	// Generating complete images (with canvas.NewRaster()) is more efficient
	// but sometimes controlling pixels directly is more convenient.
	// If your pixel data is stored in an image you can load it through the
	// NewRasterFromImage() function which will load the image to display pixel
	// perfect on screen.

	raster := canvas.NewRasterWithPixels(
		func(_, _, w, h int) color.Color {
			return color.RGBA{uint8(rand.Intn(255)),
				uint8(rand.Intn(255)),
				uint8(rand.Intn(255)), 0xff}
		})
	// // raster := canvas.NewRasterFromImage()
	// win.SetContent(raster)

	text1 := canvas.NewText("Hello", color.White)
	text2 := canvas.NewText("There", color.RGBA{150, 75, 0, 255})
	text3 := canvas.NewText("(right)", color.White)
	content := container.New(layout.NewHBoxLayout(), text1, text2, layout.NewSpacer(), text3)

	text4 := canvas.NewText("centered", color.White)
	centered := container.New(layout.NewHBoxLayout(), layout.NewSpacer(), text4, layout.NewSpacer())
	two_rows := container.New(layout.NewVBoxLayout(), content, centered)

	// big_raster := container.New(layout.NewMaxLayout(), raster)
	big_raster := container.NewMax(raster)
	images := container.New(layout.NewHBoxLayout(), big_raster, layout.NewSpacer(), image)

	img_1 := canvas.NewImageFromResource(theme.FyneLogo())
	text_over := canvas.NewText("Overlay", color.Black)
	content_max := container.New(layout.NewMaxLayout(), img_1, text_over)

	label1 := canvas.NewText("Label 1", color.Black)
	value1 := canvas.NewText("Value", color.White)
	label2 := canvas.NewText("Label 2", color.Black)
	value2 := canvas.NewText("Something", color.White)
	grid := container.New(layout.NewFormLayout(), label1, value1, label2, value2)

	remove_me := widget.NewLabel("This row will disappear.")
	box_content := container.NewVBox(
		widget.NewLabel("The top row of the VBox"),
		remove_me,
		container.NewHBox(
			widget.NewLabel("Label 1"),
			widget.NewLabel("Label 2"),
		),
	)
	box_content.Add(
		container.NewHBox(
			widget.NewButton("Add more items", func() {
				box_content.Add(widget.NewLabel("Added"))
			}),
			widget.NewButton("Remove the row", func() {
				box_content.Remove(remove_me)
			}),
		),
	)

	input := widget.NewEntry()
	input.SetPlaceHolder("Enter text...")
	inp_content := container.NewVBox(input, widget.NewButton("Save", func() {
		log.Println("Content was:", input.Text)
	}))

	data_str := binding.NewString()
	data_str.Set("Initial value")
	data_label := widget.NewLabelWithData(data_str)
	go func() {
		time.Sleep(time.Second * 2)
		data_str.Set("A new string")
	}()

	data_str_2 := binding.NewString()
	data_str_2.Set("Hi!")
	linked_labentr := container.NewVBox(
		widget.NewLabelWithData(data_str_2),
		widget.NewEntryWithData(data_str_2),
	)

	slide_1 := widget.NewSlider(0, 10)
	lab_slide_1 := widget.NewLabel("Data")
	slide_cont_1 := container.NewHBox(slide_1, lab_slide_1)

	slide_val_2 := binding.NewFloat()
	slide_2 := widget.NewSliderWithData(0, 10, slide_val_2)
	lab_slide_2 := widget.NewLabelWithData(binding.FloatToString(slide_val_2))
	slide_cont_2 := container.NewHBox(slide_2, lab_slide_2)

	slide_3 := widget.NewSlider(0, 10)
	slide_wide_3lay := container.New(layout.NewMaxLayout(), slide_3)
	// slide_wide_3con := container.NewMax(slide_3)
	lab_slide_3 := widget.NewLabel("Data")
	slide_cont_3 := container.NewHBox(slide_wide_3lay, lab_slide_3)
	// slide_cont_3bis := container.NewHBox(slide_wide_3con, lab_slide_3)
	// slide_cont_3ter := container.NewMax(slide_wide_3lay, lab_slide_3)
	// slide_cont_3qua := container.NewMax(slide_wide_3con, lab_slide_3)

	slide_4 := widget.NewSlider(0, 10)

	sample_slider_1 := NewSampleSlider(0, 10)
	sample_slider_1.OnChanged = sampleSliderOnChange

	slide_5 := widget.NewSlider(0, 10)
	lab_slide_5 := widget.NewLabel("Data")
	con_slide_5 := container.New(&wideHeader{}, slide_5, lab_slide_5)

	stack_all := container.New(layout.NewVBoxLayout(),
		two_rows,
		images,
		grid,
		content_max,
		box_content,
		inp_content,
		data_label,
		linked_labentr,
		slide_cont_1,
		slide_cont_2,
		slide_cont_3,
		// slide_cont_3bis,
		// slide_cont_3ter,
		// slide_cont_3qua,
		slide_4,
		sample_slider_1,
		widget.NewSeparator(),
		con_slide_5,
	)

	win.SetContent(stack_all)

	win.Resize(fyne.NewSize(1200, 1200))
	win.Show()
	app.Run()
}
