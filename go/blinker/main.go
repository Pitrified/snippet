package main

import (
	"flag"
	"fmt"
	"os"
)

func main() {
	fmt.Println("Welcome to the hatchine.")

	// usage:
	// ./main sample -which=ticker1
	// ./main hatch -num 500 -comm 5
	// ./main images

	hatchCmd := flag.NewFlagSet("hatch", flag.ExitOnError)
	hatchNum := hatchCmd.Int("num", 500, "Number of fireflies.")
	hatchComm := hatchCmd.Int("comm", 5, "Comm max distance on the toro.")

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
		fmt.Println("Expected 'hatch', 'image' or 'sample' subcommands.")
		os.Exit(1)
	}

	switch os.Args[1] {

	case "hatch":
		hatchCmd.Parse(os.Args[2:])
		fmt.Println("Subcommand 'hatch'")
		fmt.Println("  num:", *hatchNum)
		fmt.Println("  comm:", *hatchComm)

		hatch(*hatchNum, *hatchComm)

	case "sample":
		sampleCmd.Parse(os.Args[2:])
		fmt.Println("Subcommand 'sample'")
		fmt.Println("  which:", *sampleWhich)

		switch *sampleWhich {
		case "single":
			blinkTimeoutSingle()
		case "ticker1":
			blinkTicker1()
		case "ticker2":
			blinkTicker2()
		case "timediff":
			timeDiff()
		case "safetimer":
			blinkBlinkTimer()
		}

	case "images":
		imgCmd.Parse(os.Args[2:])
		fmt.Println("Subcommand 'images'")
		fmt.Println("  num   :", *imgNum)
		fmt.Println("  comm  :", *imgComm)
		fmt.Println("  shape :", *imgShape)
		fmt.Println("  size  :", *imgSize)

		makeImages(*imgNum, *imgComm, *imgSize)

	default:
		fmt.Println("Expected 'hatch', 'images' or 'sample' subcommands.")
		os.Exit(1)

	}
}
