package main

import (
	"encoding/csv"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"io"
	"log"
	"math"
	"os"
	"strconv"
	"time"
)

// brightness goes from 1 to 0, according to decay constant
// tau = 1 / decay
// https://www.wolframalpha.com/input/?i=e+**+%28+-x+*+1%2F50+%29+for+0+%3C+x+%3C+250
func brightness(x, decay float64) float64 {
	if x < 0 {
		return 0
	}
	return math.Exp(-x * decay)
}

// Coord in a plane
type Coord struct {
	x float64
	y float64
}

func NewCoordInt(x, y int) *Coord {
	return &Coord{float64(x), float64(y)}
}

// who and when blinked
type BlinkID struct {
	fID int
	ms  int
}

// yield the BlinkID in the file, rebuilding the minute rollover
func yieldBlinkIDs(c chan<- *BlinkID, fileName string) {

	f, err := os.Open(fileName)
	check(err)
	defer f.Close()

	r := csv.NewReader(f)

	minute := 0
	new_minute := false

	for {
		record, err := r.Read()
		if err == io.EOF {
			break
		} else if err != nil {
			log.Fatal(err)
		}
		// fmt.Printf("fID: %s s: %s ms: %s\n", record[0], record[1], record[2])

		fID, err := strconv.Atoi(record[0])
		check(err)
		sec, err := strconv.Atoi(record[1])
		check(err)
		millisec, err := strconv.Atoi(record[2])
		check(err)

		// if you see a 0 sec and new_minute is true
		// increment the minutes and set it to false
		if new_minute && sec == 0 {
			new_minute = false
			minute++
		}

		// if you see a 59 sec set new_minute to true again
		if !new_minute && sec == 59 {
			new_minute = true
		}

		ms := minute*60*1000 + sec*1000 + millisec
		c <- &BlinkID{fID, ms}
	}
	close(c)
}

// find the index of the frame after the currMs
func alignFrames(currMs int, frameDistance int) int {
	if currMs < 0 {
		return 0
		// tho it's probably a lot more messed up
	}
	for i := 0; ; i++ {
		if i*frameDistance > currMs {
			return i
		}
	}
}

// get the Coord of the Firefly in the circle
func getFireCoord(fID, nF, circleRadius int, circleCenter Coord) Coord {
	angleRad := 2 * math.Pi * float64(fID) / float64(nF)
	return Coord{
		float64(circleRadius)*math.Cos(angleRad) + circleCenter.x,
		float64(circleRadius)*math.Sin(angleRad) + circleCenter.y,
	}
}

// draw a Firefly on the image
// func drawFirefly(image, fireCoord Coord, brightness float) {
// }

// generate an image with the current state of the swarm
func generateImage(
	lastBlink map[int]int,
	fireCoords map[int]Coord,
	frameIndex int,
	frameDistance int,
	imgWidth int,
	imgHeight int,
	circleRadius int,
	circleCenter Coord,
	decay float64,
) {

	img := image.NewRGBA(image.Rect(0, 0, imgWidth, imgHeight))
	black := color.RGBA{10, 10, 10, 255}
	draw.Draw(img, img.Bounds(), &image.Uniform{black}, image.Point{0, 0}, draw.Src)

	now := frameIndex * frameDistance

	// fmt.Printf("now = %+v\n", now)
	// fmt.Printf("lastBlink = %+v\n", lastBlink)

	for fID, fireCoord := range fireCoords {
		since := now - lastBlink[fID]
		bright := brightness(float64(since), decay)
		y := uint8(255 * bright)
		if bright > 0.5 {
			fmt.Printf("fID %2d since %6d y %3d bright %f\n", fID, since, y, bright)
		}
		yellow := color.RGBA{y, y, 0, 255}
		img.Set(int(fireCoord.x), int(fireCoord.y), yellow)
	}

	// Encode as PNG.
	f, _ := os.Create("image.png")
	png.Encode(f, img)
	time.Sleep(1000 * time.Millisecond)
}

func makeImages(nF, nComm int) {
	// build circle of positions
	// parse the blinking txt file
	// build the blinking images!

	const fps = 25
	const frameDistance = 1000 / fps
	fmt.Printf("fps %v, frameDistance %v\n", fps, frameDistance)
	fmt.Printf("fps %T, frameDistance %T\n", fps, frameDistance)

	const imgWidth = 900
	const imgHeight = 600
	const circleRadius = 200
	fmt.Printf("img %vx%v, radius %v\n", imgWidth, imgHeight, circleRadius)

	circleCenter := *NewCoordInt(imgWidth/2, imgHeight/2)
	fmt.Printf("circleCenter %+v %T\n", circleCenter, circleCenter)

	fileName := fmt.Sprintf("histBlinkID_%v_%v.txt", nF, nComm)
	fmt.Printf("fileName = %v\n", fileName)

	const decay = 1.0 / 60.0
	fmt.Printf("decay %+v %T\n", decay, decay)
	_ = brightness(1, decay)

	// last blink for each Firefly, in milliseconds
	// initialized at -1s, so when computing the first brightness they are off
	lastBlink := make(map[int]int)
	// coordinates of the Firefly in the circle
	fireCoords := make(map[int]Coord)
	for i := 0; i < nF; i++ {
		lastBlink[i] = -1000
		fireCoords[i] = getFireCoord(i, nF, circleRadius, circleCenter)
	}

	lastValidBlinkMs := 0
	doneAlign := false
	frameIndex := 0

	blinkCh := make(chan *BlinkID)
	go yieldBlinkIDs(blinkCh, fileName)
	for blink := range blinkCh {
		fmt.Printf("blink = %+v\n", blink)

		// if it is the first blink, align the frameIndex
		if !doneAlign {
			frameIndex = alignFrames(blink.ms, frameDistance)
			doneAlign = true
			fmt.Printf("Start frameIndex %v at %v\n", frameIndex, frameDistance*frameIndex)
		}

		// skip out of order blinks
		if blink.ms < lastValidBlinkMs {
			continue
		}
		lastValidBlinkMs = blink.ms

		// if the current blink is after the frame instant, conclude the frame
		// with the state at the *previous* blink
		if blink.ms > frameIndex*frameDistance {

			generateImage(
				lastBlink,
				fireCoords,
				frameIndex,
				frameDistance,
				imgWidth,
				imgHeight,
				circleRadius,
				circleCenter,
				decay,
			)

			// update frameIndex
			frameIndex++
			fmt.Printf("New frameIndex %v at %v\n", frameIndex, frameDistance*frameIndex)
		}

		lastBlink[blink.fID] = blink.ms
	}

	fmt.Printf("Done.\n")
}

// if there are blinks out of order
//  ignore them (how do you know they are not in order)
//  ignore if they are older than current frame ms
