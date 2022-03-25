package main

import (
	"fmt"
	"image"
	"image/color"
	"image/png"
	"os"

	"github.com/lucasb-eyer/go-colorful"
	"golang.org/x/image/draw"
)

// CIE-L*C*h° (HCL): This is generally the most useful one; CIE-L*a*b* space in
// polar coordinates, i.e. a better HSV. H° is in [0..360], C* almost in [0..1]
// and L* as in CIE-L*a*b*.

// Blending and clamping
// https://github.com/lucasb-eyer/go-colorful/issues/14#issuecomment-324205385

// elements:
// Head
// Body
// bOdy glowing
// Wings
// wIngs glowing
// bAckground
// baCkground glowing

// blit
// to upscale
// draw.Draw(img,
// image.Rect(i*blockw, 160, (i+1)*blockw, 200),
// &image.Uniform{c1.BlendHcl(c2, float64(i)/float64(blocks-1)).Clamped()},
// image.Point{}, draw.Src)

type RangeColorHCL struct {
	H, C, Lh, Ll float64
	cHCLh, cHCLl colorful.Color
}

func NewRangeColorHCL(H, C, Lh, Ll float64) *RangeColorHCL {
	r := &RangeColorHCL{
		H:  H,
		C:  C,
		Lh: Lh,
		Ll: Ll,
		// cHCLh: colorful.Hcl(H, C, Lh),
		// cHCLl: colorful.Hcl(H, C, Ll),
		cHCLh: colorful.HSLuv(H, C, Lh),
		cHCLl: colorful.HSLuv(H, C, Ll),
	}
	return r
}

// Get the blent color.
func (r *RangeColorHCL) GetBlent(t float64) colorful.Color {
	// return r.cHCLh.BlendHcl(r.cHCLl, t)
	return r.cHCLl.BlendLuvLCh(r.cHCLh, t)
}

var elemColor = map[byte]*RangeColorHCL{
	'h': NewRangeColorHCL(20, 0.5, 0.7, 0.2),   // head
	'b': NewRangeColorHCL(36, 0.5, 0.01, 0.01), // body
	'B': NewRangeColorHCL(55, 0.9, 0.7, 0.2),   // Body glowing
	'w': NewRangeColorHCL(240, 0.7, 0.2, 0.2),  // wings
	'W': NewRangeColorHCL(240, 0.7, 0.7, 0.2),  // Wings glowing
	'a': NewRangeColorHCL(0, 0.0, 0.2, 0.2),    // background
	'A': NewRangeColorHCL(0, 0.0, 0.4, 0.2),    // bAckground glowing
	'1': NewRangeColorHCL(55, 0.9, 0.7, 0.2),   // just glow a bit
	'2': NewRangeColorHCL(55, 0.9, 0.6, 0.18),  // just glow a bit
	'3': NewRangeColorHCL(55, 0.9, 0.5, 0.16),  // just glow a bit
	'4': NewRangeColorHCL(55, 0.9, 0.4, 0.14),  // just glow a bit
	'5': NewRangeColorHCL(55, 0.9, 0.3, 0.12),  // just glow a bit
	'6': NewRangeColorHCL(55, 0.9, 0.2, 0.1),   // just glow a bit
	'7': NewRangeColorHCL(55, 0.9, 0.1, 0.08),  // just glow a bit
}

var templateFireflySingle = [][]byte{
	{'a', 'h', 'a'},
	{'W', 'b', 'W'},
	{'w', 'B', 'w'},
}

var templateFireflySingle45 = [][]byte{
	// {'a', 'W', 'h'},
	// {'W', 'B', 'W'},
	// {'B', 'W', 'a'},
	{'W', 'W', 'h'},
	{'a', 'B', 'W'},
	{'B', 'a', 'W'},
}

var templateFireflyLargeSingle = [][]byte{
	{'a', 'a', 'h', 'a', 'a'},
	{'w', 'w', 'b', 'w', 'w'},
	{'w', 'W', 'B', 'W', 'w'},
	{'w', 'A', 'B', 'A', 'w'},
	{'a', 'A', 'B', 'A', 'a'},
}

// firefly templates
var TemplateFirefly = [][][]byte{
	{
		{'a', 'h', 'a'},
		// {'w', 'b', 'w'},
		{'W', 'B', 'W'},
		{'W', 'B', 'W'},
	},
	{
		// {'a', 'W', 'h'},
		// {'W', 'B', 'W'},
		// {'B', 'W', 'a'},
		{'W', 'W', 'h'},
		{'a', 'B', 'W'},
		{'B', 'a', 'W'},
	},
}

var TemplateFireflyLarge = [][][]byte{
	{
		{'a', 'a', 'h', 'a', 'a'},
		{'W', 'W', 'b', 'W', 'W'},
		{'W', 'W', 'B', 'W', 'W'},
		{'W', 'A', 'B', 'A', 'W'},
		{'a', 'A', 'B', 'A', 'a'},
	},
	{
		{'W', 'W', 'W', 'a', 'h'},
		{'a', 'W', 'W', 'b', 'a'},
		{'a', 'A', 'B', 'W', 'W'},
		{'A', 'B', 'A', 'W', 'W'},
		{'B', 'A', 'a', 'a', 'W'},
	},
}

var TemplateFireflySpherical = [][][]byte{
	{
		{'5', '4', '4', '4', '5'},
		{'4', '3', '2', '3', '4'},
		{'4', '2', '1', '2', '4'},
		{'4', '3', '2', '3', '4'},
		{'5', '4', '4', '4', '5'},
	},
}

func tryColorful() {

	// a random color
	c := colorful.Hcl(80, 0.3, 0.5)
	fmt.Printf("RGB values: %v, %v, %v\n", c.R, c.G, c.B)

	// a random RangeColorHCL
	fmt.Printf("elemColor['O'] = %+v\n", elemColor['O'])

	keys := []byte{
		'B', 'W', 'A',
		'h', 'b', 'w', 'a',
	}

	blocks := 11
	blockw := 40
	img := image.NewRGBA(image.Rect(0, 0, blocks*blockw, blockw*len(keys)))

	for i := 0; i <= 10; i++ {
		t := float64(i) * 0.1

		for ii := 0; ii < len(keys); ii++ {

			key := keys[ii]
			col := elemColor[key].GetBlent(t)
			// fmt.Printf("elemColor[%v].GetBlent(%v) = %+v\n",
			// 	key, t, col,
			// )
			draw.Draw(img,
				image.Rect(i*blockw, ii*blockw, (i+1)*blockw, (ii+1)*blockw),
				&image.Uniform{col},
				image.Point{}, draw.Src)
		}
	}
	SavePNG("testBlend.png", img)

	fmt.Printf("templateFirefly = %+v\n", templateFireflySingle)
	fmt.Printf("templateFirefly45 = %+v\n", templateFireflySingle45)
	fmt.Printf("templateFireflyLarge = %+v\n", templateFireflyLargeSingle)

	img = image.NewRGBA(image.Rect(0, 0, 100, 100))
	H := 60.0
	for i := 0; i <= 100; i++ {
		for ii := 0; ii < 100; ii++ {
			c := float64(i) / 100
			l := float64(ii) / 100
			col := colorful.Hcl(H, c, l)
			img.SetRGBA(i, ii, color.RGBA{uint8(col.R * 255), uint8(col.G * 255), uint8(col.B * 255), 255})
		}
	}
	SavePNG("testHCL.png", img)

	img = image.NewRGBA(image.Rect(0, 0, 100, 100))
	H = 60.0
	for i := 0; i <= 100; i++ {
		for ii := 0; ii < 100; ii++ {
			s := float64(i) / 100
			v := float64(ii) / 100
			col := colorful.Hsv(H, s, v)
			img.SetRGBA(i, ii, color.RGBA{uint8(col.R * 255), uint8(col.G * 255), uint8(col.B * 255), 255})
		}
	}
	SavePNG("testHSV.png", img)

	img = image.NewRGBA(image.Rect(0, 0, 360, 100))
	s := 0.7
	for i := 0; i < 360; i++ {
		for ii := 0; ii < 100; ii++ {
			H := float64(i)
			l := float64(ii) / 100
			col := colorful.Hsv(H, s, l)
			img.SetRGBA(i, ii, color.RGBA{uint8(col.R * 255), uint8(col.G * 255), uint8(col.B * 255), 255})
		}
	}
	SavePNG("testHsvHue.png", img)

	img = image.NewRGBA(image.Rect(0, 0, 100, 100))
	H = 60.0
	for i := 0; i <= 100; i++ {
		for ii := 0; ii < 100; ii++ {
			s := float64(i) / 100
			l := float64(ii) / 100
			col := colorful.HSLuv(H, s, l)
			img.SetRGBA(i, ii, color.RGBA{uint8(col.R * 255), uint8(col.G * 255), uint8(col.B * 255), 255})
		}
	}
	SavePNG("testHSLuv.png", img)

	img = image.NewRGBA(image.Rect(0, 0, 360, 100))
	s = 0.7
	for i := 0; i < 360; i++ {
		for ii := 0; ii < 100; ii++ {
			H := float64(i)
			l := float64(ii) / 100
			col := colorful.HSLuv(H, s, l)
			// img.SetRGBA(i, ii, color.RGBA{uint8(col.R * 255), uint8(col.G * 255), uint8(col.B * 255), 255})
			r, g, b := col.Clamped().RGB255()
			// r, g, b := col.RGB255()
			img.SetRGBA(i, ii, color.RGBA{r, g, b, 255})
		}
	}
	SavePNG("testHSLuvHue.png", img)

	img = image.NewRGBA(image.Rect(0, 0, 360, 100))
	s = 0.7
	for i := 0; i < 360; i++ {
		for ii := 0; ii < 100; ii++ {
			H := float64(i)
			l := float64(ii) / 100
			col := colorful.HSLuv(H, s, l)
			blend := col.BlendHcl(col, 1)
			// img.SetRGBA(i, ii, color.RGBA{uint8(col.R * 255), uint8(col.G * 255), uint8(col.B * 255), 255})
			r, g, b := blend.Clamped().RGB255()
			// r, g, b := col.RGB255()
			img.SetRGBA(i, ii, color.RGBA{r, g, b, 255})
		}
	}
	SavePNG("testHSLuvHueBlendedHCL.png", img)

	img = image.NewRGBA(image.Rect(0, 0, 360, 100))
	s = 0.7
	for i := 0; i < 360; i++ {
		for ii := 0; ii < 100; ii++ {
			H := float64(i)
			l := float64(ii) / 100
			col := colorful.HSLuv(H, s, l)
			blend := col.BlendLuvLCh(col, 1)
			// img.SetRGBA(i, ii, color.RGBA{uint8(col.R * 255), uint8(col.G * 255), uint8(col.B * 255), 255})
			r, g, b := blend.Clamped().RGB255()
			// r, g, b := col.RGB255()
			img.SetRGBA(i, ii, color.RGBA{r, g, b, 255})
		}
	}
	SavePNG("testHSLuvHueBlendedLuvLCh.png", img)

	tmp := templateFireflyLargeSingle
	// tmp := templateFirefly
	// tmp := templateFirefly45
	steps := 11
	fireflyImg := image.NewRGBA(image.Rect(0, 0, len(tmp)*steps, len(tmp[0])))
	fmt.Printf("size = %vx%v\n", len(tmp), len(tmp[0]))
	for ti := 0; ti < steps; ti++ {
		for y := 0; y < len(tmp); y++ {
			for x := 0; x < len(tmp[0]); x++ {
				key := tmp[y][x] // this is swapped, the first row is y=0
				fmt.Printf("i, ii, key = %vx%v : %c\n", y, x, key)
				blend := elemColor[key].GetBlent(float64(ti) * 0.1)
				// fmt.Printf("i, ii, blend = %vx%v : %+v\n", y, x, blend)
				r, g, b := blend.Clamped().RGB255()
				fireflyImg.SetRGBA(x+len(tmp)*ti, y, color.RGBA{r, g, b, 255})
			}
		}
	}

	SavePNG("testFirefly.png", fireflyImg)
	pixSize := 50
	largeSize := image.Rect(0, 0, len(tmp)*pixSize*steps, len(tmp[0])*pixSize)
	dst := image.NewRGBA(largeSize)
	draw.NearestNeighbor.Scale(dst, largeSize, fireflyImg, fireflyImg.Bounds(), draw.Src, nil)
	SavePNG("testUpscaledFirefly.png", dst)

	fSize := len(tmp)
	fireflyRotImg := image.NewRGBA(image.Rect(0, 0, fSize*4, len(tmp[0])))
	for y := 0; y < fSize; y++ {
		for x := 0; x < len(tmp[0]); x++ {
			key := tmp[y][x] // this is swapped, the first row is y=0
			blend := elemColor[key].GetBlent(float64(1) * 0.1)
			r, g, b := blend.Clamped().RGB255()
			// upright
			fmt.Printf("x, y = %v, %v\n", x, y)
			fireflyRotImg.SetRGBA(x, y, color.RGBA{r, g, b, 255})
			// right
			fmt.Printf("-y+fSize-1, x = %v, %v\n", -y+fSize-1, x)
			fireflyRotImg.SetRGBA(-y+fSize-1+fSize, x, color.RGBA{r, g, b, 255})
			// bottom
			fmt.Printf("-x+fSize-1, -y+fSize-1 = %v, %v\n", -x+fSize-1, -y+fSize-1)
			fireflyRotImg.SetRGBA(-x+fSize-1+(fSize*2), -y+fSize-1, color.RGBA{r, g, b, 255})
			// left
			fmt.Printf("y, -x+fSize-1 = %v, %v\n", y, -x+fSize-1)
			fireflyRotImg.SetRGBA(y+(fSize*3), -x+fSize-1, color.RGBA{r, g, b, 255})
		}
	}
	// pixSize = 50
	// largeSize = image.Rect(0, 0, len(tmp)*pixSize*4, len(tmp[0])*pixSize)
	// dst = image.NewRGBA(largeSize)
	// draw.NearestNeighbor.Scale(dst, largeSize, fireflyRotImg, fireflyRotImg.Bounds(), draw.Src, nil)
	dst = UpscaleImg(fireflyRotImg, 50)
	SavePNG("testRotatedFirefly.png", dst)
}

// Generate an image with all the needed fireflies to use.
// horizontal (X): change the luminosity
// vertical   (Y): change the rotation
func GenBlitMap(templateFirefly [][][]byte, lLevels int) *image.RGBA {

	numTemplates := len(templateFirefly)
	fSize := len(templateFirefly[0])

	fireflyRotImg := image.NewRGBA(image.Rect(0, 0, fSize*(lLevels+1), fSize*numTemplates*4))

	// helper to read rotation directions
	rotName := []string{
		"up",
		"right",
		"down",
		"left",
	}

	// iterate over the lightness level
	for il := 0; il <= lLevels; il++ {

		// compute the lightness level in [0,1]
		l := float64(il) * 1.0 / float64(lLevels)
		fmt.Printf("l = %+v\n", l)
		// how much to shift the template right
		lSh := fSize * il

		// iterate over the template position
		for y := 0; y < fSize; y++ {
			for x := 0; x < fSize; x++ {

				// iterate over the different templates
				for it := 0; it < numTemplates; it++ {

					// get the color to use
					key := templateFirefly[it][y][x] // this is swapped, the first row is y=0
					blend := elemColor[key].GetBlent(l)
					r, g, b := blend.Clamped().RGB255()

					// how much to shift the template down
					tSh := fSize * (numTemplates - 1) * it

					// iterate over the different rotations
					for ir := 0; ir < len(rotName); ir++ {
						// get the rotated coordinates
						xr, yr := GetRotatedCoords(x, y, fSize, rotName[ir])
						// how much to shift the template right
						rSh := fSize * numTemplates * ir
						fireflyRotImg.SetRGBA(xr+lSh, yr+tSh+rSh, color.RGBA{r, g, b, 255})
					}
				}
			}
		}
	}

	dst := UpscaleImg(fireflyRotImg, 20)
	SavePNG("testBlitFirefly.png", dst)

	return fireflyRotImg
}

type Firefly struct {
	X, Y float32 // Position on the map.
	O    int16   // Orientation in degrees.
}

// orientation and lightness level
func findBlitPos(o int16, l, templateSize, rotNum int) (int, int) {

	sectorSize := int16(90 / rotNum)

	tO := o + sectorSize/2
	if tO > 360 {
		tO -= 360
	}
	rotI := tO / sectorSize

	return l * templateSize, int(rotI) * templateSize
}

func tryBlitting(blitTemplate *image.RGBA) {

	// blitSize := image.Rect(0, 0, 3, 3)

	// the world is 30x20, upscaled 3x

	img := image.NewRGBA(image.Rect(0, 0, 90, 60))
	backCol := elemColor['A'].GetBlent(1)

	draw.Draw(img,
		img.Bounds(),
		&image.Uniform{backCol},
		image.Point{}, draw.Src)

	// find the corner of the rect in the source image
	x, y := findBlitPos(0, 1, 3, 2) // == sr.Min
	// rectangle in the source image
	sr := image.Rect(x, y, x+3, y+3)
	// corner of the rect in the dest image
	dp := image.Pt(10, 10)
	// rectangle in the dest image
	dr := image.Rectangle{dp, dp.Add(sr.Size())}
	draw.Draw(img, dr, blitTemplate, sr.Min, draw.Src)

	// regular placement
	x, y = findBlitPos(45, 1, 3, 2)
	sr = image.Rect(x, y, x+3, y+3)
	dp = image.Pt(20, 10)
	dr = image.Rectangle{dp, dp.Add(sr.Size())}
	draw.Draw(img, dr, blitTemplate, sr.Min, draw.Src)

	// out of border: no problem!
	x, y = findBlitPos(135, 1, 3, 2)
	sr = image.Rect(x, y, x+3, y+3)
	dp = image.Pt(-1, -1)
	dr = image.Rectangle{dp, dp.Add(sr.Size())}
	draw.Draw(img, dr, blitTemplate, sr.Min, draw.Src)

	// out of border: no problem!
	x, y = findBlitPos(135, 1, 3, 2)
	sr = image.Rect(x, y, x+3, y+3)
	dp = image.Pt(img.Bounds().Max.X-2, img.Bounds().Max.Y-2)
	dr = image.Rectangle{dp, dp.Add(sr.Size())}
	draw.Draw(img, dr, blitTemplate, sr.Min, draw.Src)

	_, y = findBlitPos(270, 1, 3, 2)
	x = 3 * 6
	sr = image.Rect(x, y, x+3, y+3)
	dp = image.Pt(20, 20)
	dr = image.Rectangle{dp, dp.Add(sr.Size())}
	draw.Draw(img, dr, blitTemplate, sr.Min, draw.Src)

	_, y = findBlitPos(270, 1, 3, 2)
	x = 3 * 7
	sr = image.Rect(x, y, x+3, y+3)
	dp = image.Pt(25, 20)
	dr = image.Rectangle{dp, dp.Add(sr.Size())}
	draw.Draw(img, dr, blitTemplate, sr.Min, draw.Src)

	SavePNG("testBlitting.png", img)
	dst := UpscaleImg(img, 20)
	SavePNG("testBlittingUpscaled.png", dst)
	SavePNG("testBlittingUpscaled2.png", UpscaleImg(img, 2))
	SavePNG("testBlittingUpscaled3.png", UpscaleImg(img, 3))

}

func tryBlittingParallel(blitTemplate *image.RGBA) {

	// world is 300x200
	worldW, worldH := 240, 160
	// cell size
	cellSize := 40
	// upscaling factor
	scale := 5
	// size of the template
	blitSize := image.Rect(0, 0, 3, 3)
	blitSizeF32 := float32(blitSize.Bounds().Max.X)

	img := image.NewRGBA(image.Rect(0, 0, worldW*cellSize*scale, worldH*cellSize*scale))
	backCol := elemColor['A'].GetBlent(1)
	draw.Draw(img,
		img.Bounds(),
		&image.Uniform{backCol},
		image.Point{}, draw.Src)

	borderDraw := make(chan *Firefly, 100)
	borderDrawClose := make(chan bool)
	go drawFireBorder(img, borderDraw, borderDrawClose)

	// fireflies are all in the same cell
	// you just need to check if the template is crossing on the next cell
	aFirefly := &Firefly{10.1, 10.1, 0}

	// check if the firefly goes to the next cell

	// which cell the firefly is in
	cellX := int(aFirefly.X) / cellSize
	// cellY := int(firefly.Y) / cellSize

	// border of the cell in the scaled world
	right := float32((cellX + 1) * cellSize * scale)
	// bottom := (cellY + 1) * cellSize * scale

	// position of the firefly in the scaled world
	scaledX := aFirefly.X * float32(scale)
	// scaledY := firefly.Y * float32(scale)

	// NOTE TODO also check if is close to the left side
	if scaledX+blitSizeF32 > right {
		borderDraw <- aFirefly
	}
	<-borderDrawClose

}

func drawFireBorder(
	img *image.RGBA,
	borderDraw chan *Firefly,
	borderDrawClose chan bool,
) {

	// listen on borderDraw
	// when you see a nil it's over

	// signal that the drawing is done
	borderDrawClose <- true

}

func SavePNG(name string, img image.Image) {
	toimg, err := os.Create(name)
	if err != nil {
		fmt.Printf("Error: %v", err)
		return
	}
	defer toimg.Close()

	png.Encode(toimg, img)
}

// rescale image
// https://gist.github.com/logrusorgru/570d64fd6a051e0441014387b89286ca
func UpscaleImg(img image.Image, pixSize int) *image.RGBA {
	largeSize := image.Rect(0, 0, img.Bounds().Dx()*pixSize, img.Bounds().Dy()*pixSize)
	dst := image.NewRGBA(largeSize)
	draw.NearestNeighbor.Scale(dst, largeSize, img, img.Bounds(), draw.Src, nil)
	return dst
}

func GetRotatedCoords(x, y, size int, rot string) (int, int) {
	switch rot {
	case "up":
		return x, y
	case "right":
		return -y + size - 1, x
	case "down":
		return -x + size - 1, -y + size - 1
	case "left":
		return y, -x + size - 1
	}
	// this should never happen lol
	return 0, 0
}

// rescale image
// https://gist.github.com/logrusorgru/570d64fd6a051e0441014387b89286ca
func main() {
	fmt.Println("vim-go")
	tryColorful()

	// number of lightness levels (-1)
	lLevels := 50

	blit := GenBlitMap(TemplateFirefly, lLevels)
	tryBlitting(blit)

	blit = GenBlitMap(TemplateFireflySpherical, lLevels)
	tryBlittingParallel(blit)
}
