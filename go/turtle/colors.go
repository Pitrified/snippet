package turtle

import "image/color"

var (
	Black     = color.RGBA{0, 0, 0, 255}
	SoftBlack = color.RGBA{10, 10, 10, 255}
	White     = color.RGBA{255, 255, 255, 255}

	Red   = color.RGBA{255, 0, 0, 255}
	Green = color.RGBA{0, 255, 0, 255}
	Blue  = color.RGBA{0, 0, 255, 255}

	Cyan    = color.RGBA{0, 255, 255, 255}
	Magenta = color.RGBA{255, 0, 255, 255}
	Yellow  = color.RGBA{255, 255, 0, 255}
)

// not really colors but still useful...
var (
	East  = 0.0
	Right = 0.0
	North = 90.0
	Up    = 90.0
	West  = 180.0
	Left  = 180.0
	South = 270.0
	Down  = 270.0
)
