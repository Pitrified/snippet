package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"

	"github.com/Pitrified/go-turtle"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/layout"
)

func main() {
	fmt.Println("vim-go")

	t := turtle.New()
	fmt.Println("T:", t)

	app := app.New()
	win := app.NewWindow("Hello")

	width := 1920
	height := 1080
	imgColor := color.RGBA{45, 45, 65, 255}
	img := image.NewRGBA(image.Rect(0, 0, width, height))
	draw.Draw(img, img.Bounds(), &image.Uniform{imgColor}, image.Point{0, 0}, draw.Src)

	img_2 := canvas.NewImageFromImage(img)
	// img_2 := canvas.NewImageFromResource(theme.FyneLogo())
	img_2.FillMode = canvas.ImageFillOriginal
	// img_2.FillMode = canvas.ImageFillContain
	// img_2.SetMinSize(fyne.Size{Width: 900, Height: 600})
	img_2.SetMinSize(fyne.Size{Width: 1920, Height: 1080})
	// img_2.SetMinSize(fyne.Size{Width: 1600, Height: 900})

	text1 := canvas.NewText("Hello", color.White)

	// content := container.New(layout.NewHBoxLayout(), image, text1)

	// img_1 := canvas.NewImageFromResource(theme.FyneLogo())
	// img_1.FillMode = canvas.ImageFillOriginal
	// img_1.SetMinSize(fyne.Size{Width: 500, Height: 500})
	// raster := canvas.NewRasterWithPixels(
	// 	func(_, _, w, h int) color.Color {
	// 		return color.RGBA{uint8(rand.Intn(255)),
	// 			uint8(rand.Intn(255)),
	// 			uint8(rand.Intn(255)), 0xff}
	// 	})
	// big_raster := container.NewMax(raster)
	// images := container.New(layout.NewHBoxLayout(),
	// big_raster,
	// layout.NewSpacer(),
	// img_1,
	// img_2,
	// text1,
	// )

	// stack_all := container.New(layout.NewVBoxLayout(),
	// images,
	// )

	borderL := container.New(
		layout.NewBorderLayout(nil, nil, nil, text1),
		text1,
		img_2,
	)

	// finalContent := content
	// finalContent := stack_all
	// finalContent := images
	finalContent := borderL
	win.SetContent(finalContent)

	// win.Resize(fyne.NewSize(1200, 1200))
	win.Show()
	app.Run()
}
