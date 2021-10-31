package circle

import (
	"blinker/utils"
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
	"path/filepath"
	"strconv"
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
	utils.Check(err)
	defer f.Close()

	r := csv.NewReader(f)
	// manually check the number of fields
	r.FieldsPerRecord = -1

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

		if len(record) != 3 || len(record[2]) == 0 {
			break
		}

		fID, err := strconv.Atoi(record[0])
		utils.Check(err)
		sec, err := strconv.Atoi(record[1])
		utils.Check(err)
		millisec, err := strconv.Atoi(record[2])
		utils.Check(err)

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
func drawFirefly(img *image.RGBA, fireCoord Coord, brightness float64) {
	ix, iy := int(fireCoord.x), int(fireCoord.y)

	brightMax := uint8(255 * brightness)
	yellow := color.RGBA{brightMax, brightMax, 0, 255}
	img.Set(ix, iy, yellow)

	// return
	brightMid := uint8(255 * brightness * 0.8)
	yellow = color.RGBA{brightMid, brightMid, 0, 255}
	img.Set(ix+1, iy, yellow)
	img.Set(ix-1, iy, yellow)
	img.Set(ix, iy+1, yellow)
	img.Set(ix, iy-1, yellow)

	brightMin := uint8(255 * brightness * 0.5)
	yellow = color.RGBA{brightMin, brightMin, 0, 255}
	img.Set(ix+1, iy+1, yellow)
	img.Set(ix-1, iy+1, yellow)
	img.Set(ix+1, iy-1, yellow)
	img.Set(ix-1, iy-1, yellow)
}

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
	outImgDir string,
	outImgTempl string,
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
		drawFirefly(img, fireCoord, bright)
	}

	// Encode as PNG.
	outImgName := fmt.Sprintf(outImgTempl, frameIndex)
	outImgPath := filepath.Join(outImgDir, outImgName)
	// fmt.Printf("    outImgPath = %+v\n", outImgPath)
	f, _ := os.Create(outImgPath)
	defer f.Close()
	png.Encode(f, img)
}

func MakeImages(nF, nComm int, imgSizeType string) {
	// build circle of positions
	// parse the blinking txt file
	// build the blinking images!

	// framerate
	const fps = 25
	const frameDistance = 1000 / fps
	fmt.Printf("fps %v, frameDistance %v\n", fps, frameDistance)

	// image size and circle size
	var imgWidth, imgHeight int
	var circleRadius int
	switch imgSizeType {
	case "1K":
		imgWidth = 1920
		imgHeight = 1080
		circleRadius = 480
	case "4K":
		imgWidth = 3840
		imgHeight = 2160
		circleRadius = 480 * 2
	case "1200":
		imgWidth = 1200
		imgHeight = 1200
		circleRadius = 480
	default:
		imgWidth = 1200
		imgHeight = 1200
		circleRadius = 480
	}

	fmt.Printf("img %vx%v, radius %v\n", imgWidth, imgHeight, circleRadius)
	circleCenter := *NewCoordInt(imgWidth/2, imgHeight/2)
	fmt.Printf("circleCenter %+v %T\n", circleCenter, circleCenter)

	// brightness decay
	const decay = 1.0 / 180.0
	fmt.Printf("decay %+v %T\n", decay, decay)

	// input file
	baseHistDir := "histBlink"
	outHistFileName := fmt.Sprintf("histBlinkID_%v_%v.txt", nF, nComm)
	fullHistFile := filepath.Join(baseHistDir, outHistFileName)
	fmt.Printf("fullHistFile = %v\n", fullHistFile)

	// create the base image dir if it does not exist
	baseImgDir := "images"
	err := utils.EnsureDir(baseImgDir, 0775)
	utils.Check(err)

	// remove and re-create the output dir
	outImgDirName := fmt.Sprintf("images_%v_%v", nF, nComm)
	outImgDir := filepath.Join(baseImgDir, outImgDirName)
	err = os.RemoveAll(outImgDir)
	utils.Check(err)
	err = os.Mkdir(outImgDir, 0775)
	utils.Check(err)

	// output name template
	outImgTempl := "frame_%04d.png"

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
	go yieldBlinkIDs(blinkCh, fullHistFile)
	for blink := range blinkCh {
		// fmt.Printf("blink = %+v\n", blink)

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
				frameIndex, frameDistance,
				imgWidth, imgHeight,
				circleRadius, circleCenter,
				decay,
				outImgDir, outImgTempl,
			)

			// update frameIndex
			frameIndex++
			fmt.Printf("New frameIndex %4d at %6d\n", frameIndex, frameDistance*frameIndex)
		}

		lastBlink[blink.fID] = blink.ms
	}

	fmt.Printf("Done.\n")
}

// if there are blinks out of order
//  ignore them (how do you know they are not in order)
//  ignore if they are older than current frame ms
