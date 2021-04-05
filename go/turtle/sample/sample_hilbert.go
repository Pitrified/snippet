package main

import (
	"fmt"
	"image/color"
	"math"

	"example.com/turtle"
)

func hilbertInstructions(
	level int,
	remaining string,
	instructions chan<- string,
	rules map[string]string,
) string {

	// fmt.Printf("level = %v\n", level)

	for len(remaining) > 0 {
		curChar := remaining[0]
		remaining = remaining[1:]
		// fmt.Printf("curChar %c remaining %v\n", curChar, remaining)

		switch curChar {

		case '|':
			return remaining

		case '+':
			instructions <- "L"
		case '-':
			instructions <- "R"

		case 'F':
			instructions <- "F"

		case 'A':
			if level > 0 {
				remaining = rules["A"] + "|" + remaining
				remaining = hilbertInstructions(
					level-1, remaining, instructions, rules)
			}
		case 'B':
			if level > 0 {
				remaining = rules["B"] + "|" + remaining
				remaining = hilbertInstructions(
					level-1, remaining, instructions, rules)
			}
		}
	}

	close(instructions)
	return ""
}

func sampleHilbert() {
	// imgWidth := 1080
	// imgHeight := 1080
	imgWidth := 2080
	imgHeight := 2080
	tw := turtle.NewTurtleWorld(imgWidth, imgHeight)

	tw.SetPos(turtle.Position{40, 40})
	tw.PenDown()
	tw.SetColor(color.RGBA{150, 75, 0, 255})

	// rewrite rules
	rules := map[string]string{
		"A": "+BF-AFA-FB+",
		"B": "-AF+BFB+FA-",
	}

	// remaining commands to do
	remaining := rules["A"]

	// recursion level
	level := 7

	// receive the instructions here
	instructions := make(chan string)

	// will produce instructions on the channel
	go hilbertInstructions(level, remaining, instructions, rules)

	// how much to move Forward
	// segmentLen := 10.0
	segmentLen := float64(imgWidth-80) / (math.Exp2(float64(level-1))*4 - 1)
	den := float64(2.0 ^ (level+1)*4)
	fmt.Printf("den = %+v\n", den)
	fmt.Printf("segmentLen = %+v\n", segmentLen)

	for cmd := range instructions {
		// fmt.Printf("cmd = %+v\n", cmd)
		switch cmd {
		case "F":
			tw.Forward(segmentLen)
		case "R":
			tw.Rigth(90)
		case "L":
			tw.Left(90)
		}
	}

	outImgName := "sample_hilbert.png"
	tw.SaveImage(outImgName)
}
