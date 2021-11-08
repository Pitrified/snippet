package main

import (
	"flag"
	"fmt"
	"os"

	"blinker/cellfire"
	"blinker/circle"
	"blinker/firefly"
)

func main() {
	fmt.Println("Welcome to the hatchine.")

	// usage:
	// ./main sample -which=ticker1
	// ./main circle -num 500 -comm 5
	// ./main images
	// ./main fireflies
	// ./main cellfire

	circleCmd := flag.NewFlagSet("circle", flag.ExitOnError)
	circleNum := circleCmd.Int("num", 500, "Number of fireflies.")
	circleComm := circleCmd.Int("comm", 5, "Comm max distance on the toro.")

	sampleCmd := flag.NewFlagSet("sample", flag.ExitOnError)
	sampleWhich := sampleCmd.String("which", "timediff", "Which sample to run.")

	imgCmd := flag.NewFlagSet("images", flag.ExitOnError)
	imgNum := imgCmd.Int("num", 500, "Number of fireflies.")
	imgComm := imgCmd.Int("comm", 5, "Comm max distance on the toro.")
	imgShape := imgCmd.String("shape", "circle",
		"Shape of the swarm. Valid values: 'circle', 'hilbert'.",
	)
	imgSize := imgCmd.String("size", "1K",
		"Size of the images. Valid values: '1K', '4K', '1200'.",
	)

	if len(os.Args) < 2 {
		fmt.Println("Expected 'circle', 'images', 'fireflies', 'cellfire' or 'sample' subcommands.")
		os.Exit(1)
	}

	switch os.Args[1] {

	case "circle":
		circleCmd.Parse(os.Args[2:])
		fmt.Println("Subcommand 'circle'")
		fmt.Println("  num:", *circleNum)
		fmt.Println("  comm:", *circleComm)

		circle.Hatch(*circleNum, *circleComm)

	case "sample":
		sampleCmd.Parse(os.Args[2:])
		fmt.Println("Subcommand 'sample'")
		fmt.Println("  which:", *sampleWhich)

		switch *sampleWhich {
		case "single":
			circle.BlinkTimeoutSingle()
		case "ticker1":
			circle.BlinkTicker1()
		case "ticker2":
			circle.BlinkTicker2()
		case "timediff":
			circle.TimeDiff()
		case "safetimer":
			circle.BlinkBlinkTimer()
		}

	case "images":
		imgCmd.Parse(os.Args[2:])
		fmt.Println("Subcommand 'images'")
		fmt.Println("  num   :", *imgNum)
		fmt.Println("  comm  :", *imgComm)
		fmt.Println("  shape :", *imgShape)
		fmt.Println("  size  :", *imgSize)

		circle.MakeImages(*imgNum, *imgComm, *imgSize)

	case "fireflies":
		firefly.CreateFireflies()

	case "cellfire":
		// cellfire.StartFire(2, 2, 50, 100)
		// cellfire.StartFire(2, 2, 50, 300) // rad 20
		// cellfire.StartFire(2, 2, 50, 500)
		// cellfire.StartFire(2, 2, 50, 1_000)
		// cellfire.StartFire(2, 2, 50, 10_000)
		// cellfire.StartFire(4, 4, 100, 1_000)
		// cellfire.StartFire(8, 8, 50, 8_000)
		// cellfire.StartFire(16, 16, 100, 50_000)
		// cellfire.StartFire(16, 16, 200, 50_000) // rad 50, 10s in 8s, fails
		cellfire.StartFire(16, 16, 200, 50_000) // rad 100, 10s in 7s
		// cellfire.StartFire(16, 16, 400, 250_000) // rad 100, 25s in 2m44s
		// cellfire.StartFire(32, 32, 200, 250_000) // rad 50, 10s in 43s, fails
		// cellfire.StartFire(32, 32, 200, 250_000) // rad 100, 25s in 1m34s
		// cellfire.StartFire(64, 64, 100, 250_000) // rad 100, 25s in 1m57s
		// cellfire.StartFire(32, 32, 50, 50_000)

	default:
		fmt.Println("Expected 'circle', 'images', 'fireflies', 'cellfire' or 'sample' subcommands.")
		os.Exit(1)

	}
}
