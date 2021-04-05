package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"

	"example.com/turtle"
)

func sampleTurtle1() {

	// turtle has valid zero values
	t := turtle.Turtle{}
	fmt.Printf("t = %+v\n", t)

	// note that here the color is nil
	tp1 := turtle.TurtlePen{}
	fmt.Printf("tp1 = %+v\n", tp1)

	// need to create it manually
	tp2 := *turtle.NewTurtlePen()
	fmt.Printf("tp2 = %+v\n", tp2)

	imgWidth := 1920
	imgHeight := 1080
	img := image.NewRGBA(image.Rect(0, 0, imgWidth, imgHeight))
	black := color.RGBA{10, 10, 10, 255}
	draw.Draw(img, img.Bounds(), &image.Uniform{black}, image.Point{0, 0}, draw.Src)
	fmt.Printf("img.Bounds().Max.Y = %+v\n", img.Bounds().Max.Y)

	tw := *turtle.NewTurtleWorld(img)
	fmt.Printf("tw = %+v\n", tw)

	centerPos := turtle.NewPositionInt(imgWidth/2, imgHeight/2)
	tw.SetPos(centerPos)

	tw.PenDown()
	tw.Forward(100)
	tw.Rigth(90)
	tw.SetColor(turtle.Red)
	tw.Forward(100)
	tw.Rigth(90)
	tw.SetColor(turtle.Green)
	tw.Forward(100)
	tw.Rigth(90)
	tw.SetColor(turtle.Blue)
	tw.Forward(100)
	tw.Rigth(90)

	tw.PenUp()
	tw.Forward(200)
	tw.Left(360)

	tw.PenDown()
	tw.Rigth(30)
	tw.SetColor(turtle.Cyan)
	tw.Forward(100)
	tw.Rigth(90)
	tw.SetColor(turtle.Magenta)
	tw.Forward(200)
	tw.Rigth(90)
	tw.SetColor(turtle.Yellow)
	tw.Forward(300)
	tw.Rigth(90)
	tw.SetColor(color.RGBA{123, 24, 76, 255})
	tw.Forward(400)

	// Encode as PNG. (MAYBE it's a method of TurtleWorld)
	outImgName := "sample_world.png"
	tw.SaveImage(outImgName)
	fmt.Printf("tw = %+v\n", tw)
}

func main() {
	fmt.Println("Welcome to the Tungle.")
	sampleTurtle1()
}
