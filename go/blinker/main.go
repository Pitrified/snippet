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
	// ./main image

	hatchCmd := flag.NewFlagSet("hatch", flag.ExitOnError)
	hatchNum := hatchCmd.Int("num", 500, "Number of fireflies.")
	hatchComm := hatchCmd.Int("comm", 5, "Comm max distance on the toro.")

	sampleCmd := flag.NewFlagSet("sample", flag.ExitOnError)
	sampleWhich := sampleCmd.String("which", "timediff", "Which sample to run.")

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

	default:
		fmt.Println("Expected 'hatch', 'image' or 'sample' subcommands.")
		os.Exit(1)

	}
}
