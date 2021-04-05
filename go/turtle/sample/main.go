package main

import (
	"fmt"
	"image/color"

	"example.com/turtle"
)

func sampleTurtle1() {

	// turtle has valid zero values
	t := turtle.Turtle{}
	fmt.Printf("t = %+v\n", t)

	// note that here the color is nil
	tp1 := turtle.TurtlePen{}
	fmt.Printf("tp1 = %+v\n", tp1)

	// need to create it like this
	tp2 := *turtle.NewTurtlePen()
	fmt.Printf("tp2 = %+v\n", tp2)

	// create an empty world
	imgWidth := 1920
	imgHeight := 1080
	tw := turtle.NewTurtleWorld(imgWidth, imgHeight)
	fmt.Printf("tw = %+v\n", tw)

	tw.SetPos(turtle.NewPositionInt(imgWidth/4, imgHeight/2))

	// a square
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
	tw.Forward(150)
	tw.Left(360)

	// a thing?
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

	tw.PenUp()
	tw.SetPos(turtle.Position{1200, 500})

	// draw a circle with increasing brightness
	tw.PenDown()
	tw.SetHeading(turtle.North)
	for i := 0; i < 360; i++ {
		val := uint8(255.0 / 360.0 * float64(i))
		tw.SetColor(color.RGBA{val, val / 2, 0, 255})
		tw.Rigth(1)
		tw.Forward(4)
	}

	// Encode as PNG.
	outImgName := "sample_world.png"
	tw.SaveImage(outImgName)

	// current status
	fmt.Printf("tw = %+v\n", tw)
}

func main() {
	fmt.Println("Welcome to the Tungle.")
	sampleTurtle1()
}
