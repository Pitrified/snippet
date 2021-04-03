package main

import (
	"fmt"
	"image"
	"image/color"
	"image/png"
	"io"
	"math"
	"math/cmplx"
	"math/rand"
	"os"
	"runtime"
	"strings"
	"time"

	"golang.org/x/tour/wc"
)

// https://tour.golang.org/basics/4 5
func add(x, y int) int {
	return x + y
}

// https://tour.golang.org/basics/6
func swap(x, y string) (string, string) {
	return y, x
}

// https://tour.golang.org/basics/8
var c, python, java bool

// https://tour.golang.org/basics/11
var (
	ToBe   bool       = false
	MaxInt uint64     = 1<<64 - 1
	z      complex128 = cmplx.Sqrt(-5 + 12i)
)

// a tourBasic of go
// BASICS https://tourBasic.golang.org/basics/1
func tourBasic() {
	fmt.Println("Start tourBasic.")

	rand.Seed(123)
	fmt.Println("My favorite number is", rand.Intn(10), add(1, 2))

	a, b := swap("hello", "world")
	fmt.Println(a, b)

	// declare vars
	var i int = 101
	d := 101
	fmt.Println(i, c, d, python, java)

	fmt.Printf("Type: %T Value: %v\n", ToBe, ToBe)
	fmt.Printf("Type: %T Value: %v\n", MaxInt, MaxInt)
	fmt.Printf("Type: %T Value: %v\n", z, z)

	// zero value
	var zi int
	var zf float64
	var zb bool
	var zs string
	fmt.Printf("%v %v %v %q\n", zi, zf, zb, zs)

	// cast
	var x, y int = 3, 4
	var f float64 = math.Sqrt(float64(x*x + y*y))
	var z uint = uint(f)
	fmt.Println(x, y, z)

	// const
	const Truth = true
	fmt.Println("Go rules?", Truth)
}

// -----------------------------------------------------------------------------

// https://tour.golang.org/flowcontrol/5
func sqrt(x float64) string {
	if x < 0 {
		return sqrt(-x) + "i"
	}
	return fmt.Sprint(math.Sqrt(x))
}

// https://tour.golang.org/flowcontrol/6
func pow(x, n, lim float64) float64 {
	// if can have a statement to execute before the condition
	if v := math.Pow(x, n); v < lim {
		return v
	} else {
		fmt.Printf("%g >= %g\n", v, lim)
	}
	return lim
}

// https://tour.golang.org/flowcontrol/8
// Newton method z -= (z*z - x) / (2*z)
func artisanalSqrt(x float64) float64 {
	// first guess for z
	z := 1.0
	for {
		delta := (z*z - x) / (2 * z)
		fmt.Println("delta", delta)
		if math.Abs(delta) < 0.000000001 {
			return z
		}
		z -= delta
	}
}

// https://tour.golang.org/flowcontrol/13
func sampleDefer() {
	// deferred calls are executed in last-in-first-out order
	fmt.Println("counting")
	for i := 0; i < 3; i++ {
		defer fmt.Println(i)
	}
	fmt.Println("done")
}

// https://tour.golang.org/flowcontrol/1
func tourFlow() {
	fmt.Println("Start tourFlow.")

	// for
	sum := 0
	for i := 0; i < 10; i++ {
		sum += i
	}
	fmt.Println(sum)

	// while
	sum = 1
	for sum < 1000 {
		sum += sum
	}
	fmt.Println(sum)

	fmt.Println(sqrt(2), sqrt(-4))
	fmt.Println(pow(3, 2, 10), pow(3, 3, 20))

	origSqrt := math.Sqrt(2)
	artSqrt := artisanalSqrt(2)
	fmt.Printf("artSqrt = %f, error %f\n", artSqrt, artSqrt-origSqrt)

	// switch
	fmt.Print("Go runs on ")
	switch os := runtime.GOOS; os {
	case "darwin":
		fmt.Println("OS X.")
	case "linux":
		fmt.Println("Linux.")
	default:
		// freebsd, openbsd, plan9, windows...
		fmt.Printf("%s.\n", os)
	}

	// https://tour.golang.org/flowcontrol/10
	today := time.Now().Weekday()
	fmt.Println("Today is", today)
	fmt.Println("Tomorrow is", today+1)
	fmt.Printf("today = %+v type %T\n", today, today)

	fmt.Println("When's Saturday?")
	switch time.Saturday {
	case today + 0:
		fmt.Println("Today.")
	case today + 1:
		fmt.Println("Tomorrow.")
	case today + 2:
		fmt.Println("In two days.")
	default:
		fmt.Println("Too far away.")
	}

	sampleDefer()
}

// -----------------------------------------------------------------------------

type Vertex struct {
	X float64
	Y float64
}

// https://tour.golang.org/moretypes/11
func printSlice(s []int) {
	fmt.Printf("len=%d cap=%d %v\n", len(s), cap(s), s)
}

// https://tour.golang.org/moretypes/18
func Pic(dx, dy int) [][]uint8 {
	var mypic = make([][]uint8, dx)

	for i := 0; i < dx; i++ {
		mypic[i] = make([]uint8, dy)
		for j := 0; j < dy; j++ {
			mypic[i][j] = uint8(i * j)
		}
	}
	return mypic
}

// https://tour.golang.org/moretypes/23
func WordCount(s string) map[string]int {
	words := strings.Fields(s)
	count := make(map[string]int)
	for _, word := range words {
		_, in := count[word]
		if !in {
			count[word] = 0
		}
		count[word]++
	}
	return count
}

// https://tour.golang.org/moretypes/24
func computeAt(
	fn func(float64, float64) float64,
	x float64,
	y float64) float64 {
	return fn(x, y)
}

// https://tour.golang.org/moretypes/25
func adder() func(int) int {
	sum := 0
	return func(x int) int {
		sum += x
		return sum
	}
}

// https://tour.golang.org/moretypes/26
// fibonacci is a function that returns
// a function that returns an int.
func fibonacci() func() int {
	x0 := 0
	x1 := 1
	return func() int {
		next := x0 + x1
		x0 = x1
		x1 = next
		return next
	}
}

// https://tour.golang.org/moretypes/2
func tourTypes() {
	fmt.Println("Start tourTypes.")

	i, j := 42, 2701

	pi := &i         // point to i
	fmt.Println(*pi) // read i through the pointer
	fmt.Println(pi)  // value of pointer pi
	*pi = 21         // set i through the pointer
	fmt.Println(i)   // see the new value of i

	pj := &j       // point to j
	*pj = *pj / 37 // divide j through the pointer
	fmt.Println(j) // see the new value of j

	// structs
	v := Vertex{1, 2}
	v.X = 4
	fmt.Printf("%v\n", v)  // the instance
	fmt.Printf("%+v\n", v) // with field names
	fmt.Printf("%#v\n", v) // Go syntax representation of the value

	pv := &v
	// magic without explicit dereference
	// (*pv).X = 1e9
	pv.X = 1e2
	fmt.Printf("%#v\n", pv) // Go syntax representation of the value

	// array - slices

	// The type [n]T is an array of n values of type T.
	primes := [6]int{2, 3, 5, 7, 11, 13}
	fmt.Println(primes)
	// The type []T is a slice with elements of type T.
	var s []int = primes[1:4]
	fmt.Println(s)
	s = primes[2:5]
	fmt.Println(s)
	// A slice does not store any data, it just describes a section of an
	// underlying array. Changing the elements of a slice modifies the
	// corresponding elements of its underlying array.
	names := [4]string{
		"John",
		"Paul",
		"George",
		"Ringo",
	}
	fmt.Println(names)
	a := names[0:2]
	b := names[1:3]
	fmt.Println(a, b)
	b[0] = "XXX"
	fmt.Println(a, b)
	fmt.Println(names)

	// A slice literal is like an array literal without the length.
	// This is an array literal:
	ab := [3]bool{true, true, false}
	// This creates the same array as above, then builds a slice that references it:
	sb := []bool{true, true, false}
	// A slice can have automatic bounds
	ssb := ab[:]
	fmt.Println(ab, sb, ssb)

	// A slice has both a length and a capacity.
	// The length of a slice is the number of elements it contains.
	// The capacity of a slice is the number of elements in the underlying
	// array, counting from the first element in the slice.
	printSlice(primes[:])
	printSlice(primes[3:5])
	printSlice(primes[1:3])
	var nil_slice []int
	printSlice(nil_slice)

	// Create a tic-tac-toe board.
	board := [][]string{
		[]string{"_", "_", "_"},
		[]string{"_", "_", "_"},
		[]string{"_", "_", "_"},
	}
	// The players take turns.
	board[0][0] = "X"
	board[2][2] = "O"
	board[1][2] = "X"
	board[1][0] = "O"
	board[0][2] = "X"
	for i := 0; i < len(board); i++ {
		fmt.Printf("%s\n", strings.Join(board[i], " "))
	}

	// range to iterate over a slice or a map
	for i, line := range board {
		fmt.Printf("%d: %s\n", i, strings.Join(line, " "))
	}

	// append
	sprimes := primes[:]
	sprimes = append(sprimes, 17)
	printSlice(sprimes)

	// works on the tour page
	// pic.Show(Pic)

	// maps
	m := make(map[string]Vertex)
	m["Bell Labs"] = Vertex{40, -74}
	fmt.Println(m["Bell Labs"])

	// can skip the type if it's just the name
	m = map[string]Vertex{
		"Bell Labs": {40, -74},
		"Google":    {37, -122},
	}

	// remove an element
	fmt.Println("The value:", m["Bell Labs"])
	delete(m, "Bell Labs")
	fmt.Println("The value:", m["Bell Labs"])
	v, ok := m["Bell Labs"]
	fmt.Println("The value:", v, "Present?", ok)

	// exercise on maps
	wc.Test(WordCount)

	// func are values
	hypot := func(x, y float64) float64 {
		return math.Sqrt(x*x + y*y)
	}
	fmt.Println(computeAt(hypot, 3, 4))

	// closure: func that uses variables from outside its body
	// each adder has its own sum
	pos, neg := adder(), adder()
	for i := 0; i < 5; i++ {
		fmt.Println(pos(i), neg(-2*i))
	}

	f := fibonacci()
	for i := 0; i < 6; i++ {
		fmt.Println(f())
	}
}

// -----------------------------------------------------------------------------

// You can define methods on types.
// A method is a function with a special receiver argument.
// The receiver appears in its own argument list between the func keyword and
// the method name.
func (v Vertex) Abs2() float64 {
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}

func (v Vertex) Abs1() float64 {
	return math.Abs(v.X) + math.Abs(v.Y)
}

// with a pointer receiver, Scale operates on the instance, not on a copy
func (v *Vertex) Scale(f float64) {
	if v == nil {
		fmt.Println("Cannot scale a nil *Vertex")
		return
	}
	v.X = v.X * f
	v.Y = v.Y * f
}

// with blackjack
type MyFloat float64

func (f MyFloat) Abs1() float64 {
	if f < 0 {
		return float64(-f)
	}
	return float64(f)
}

// An interface type is defined as a set of method signatures.
type Abser interface {
	Abs1() float64
	Abs2() float64
}

type Scaler interface {
	Scale(float64)
}

// every type implements Omni
// saner with interface{}
// https://tour.golang.org/methods/14
type Omni interface {
}

// func describe(o Omni) {
func describe(o interface{}) {
	fmt.Printf("D (%v, %T)\n", o, o)
}

func typeSwitch(i interface{}) {
	switch v := i.(type) {
	case int:
		fmt.Printf("Twice %v is %v\n", v, v*2)
	case string:
		fmt.Printf("%q is %v bytes long\n", v, len(v))
	default:
		fmt.Printf("I don't know about type %T!\n", v)
	}
}

type IPAddr [4]byte

func (p IPAddr) String() string {
	return fmt.Sprintf("%v.%v.%v.%v", p[0], p[1], p[2], p[3])
}

type IPError struct {
	Which IPAddr
	What  string
}

// https://tour.golang.org/methods/19
func (p *IPError) Error() string {
	return fmt.Sprintf("IPError at %v, %v", p.Which, p.What)
}

func (p IPAddr) FakeSetFirst(v int) (IPAddr, error) {
	if v > 255 {
		fmt.Println("Too big, erroring")
		return p, &IPError{p, "Too big"}
	}
	return p, nil
}

// https://tour.golang.org/methods/20
type ErrNegativeSqrt float64

func (e ErrNegativeSqrt) Error() string {
	return fmt.Sprintf("Cannot Sqrt negative number: %v", float64(e))
}

func ArtisanalSqrtErrored(x float64) (float64, error) {
	if x < 0 {
		return 0, ErrNegativeSqrt(x)
	}
	// first guess for z
	z := 1.0
	for {
		delta := (z*z - x) / (2 * z)
		fmt.Println("delta", delta)
		if math.Abs(delta) < 0.000000001 {
			return z, nil
		}
		z -= delta
	}
}

type rot13Reader struct {
	r io.Reader
}

// type rot13ReaderError struct {
// 	arg byte
// 	why string
// }

// func (e *rot13ReaderError) Error() string {
// 	return fmt.Sprintf("Cannot rot13: %v, %v", e.arg, e.why)
// }

func (rr rot13Reader) Read(b []byte) (int, error) {
	n, err := rr.r.Read(b)
	// fmt.Printf("Read from reader n = %v err = %v b = %v\n", n, err, b)
	if err == io.EOF {
		return 0, io.EOF
	} else if err != nil {
		return 0, err // propagate the error
	}
	for i := range b {
		// oldb := b[i]
		// fmt.Printf("oldb = %+v %q\n", oldb, oldb)
		switch {
		case b[i] < 65:
			// return 0, &rot13ReaderError{b[i], "Too low."}
		case b[i] < 65+13:
			b[i] += 13
			// fmt.Printf("case 1 b[i] = %+v %q\n", b[i], b[i])
		case b[i] < 65+2*13:
			b[i] -= 13
			// fmt.Printf("case 2 b[i] = %+v %q\n", b[i], b[i])
		case b[i] < 97:
		case b[i] < 97+13:
			b[i] += 13
			// fmt.Printf("case 3 b[i] = %+v %q\n", b[i], b[i])
		case b[i] < 97+2*13:
			b[i] -= 13
			// fmt.Printf("case 4 b[i] = %+v %q\n", b[i], b[i])
		}
	}
	return n, nil
}

// https://tour.golang.org/methods/25
type Image struct {
	width  int
	height int
}

func (i Image) ColorModel() color.Model {
	return color.RGBAModel
}

func (i Image) Bounds() image.Rectangle {
	return image.Rect(0, 0, i.width, i.height)
}

func (i Image) At(x, y int) color.Color {
	v := uint8(x * y)
	return color.RGBA{v, v, 255, 255}
}

// https://tour.golang.org/methods/1
func tourMethods() {
	fmt.Println("Start tourMethods.")

	v := Vertex{3.123, 4.123}
	fmt.Println(v.Abs2())
	v.Scale(3)
	fmt.Println(v.Abs2())
	// scale actually had a pointer receiver
	p := &v
	p.Scale(10)
	fmt.Println(p.Abs2())
	// so it does under the hood
	(&v).Scale(5)
	fmt.Println(v.Abs2())
	// and the same thing is happening with Abs2 and the pointer
	// (*p).Abs2()

	f := MyFloat(-math.Sqrt2)
	fmt.Println(f, f.Abs1())

	// Vertex implements Abser
	// *Vertex does not
	var a Abser
	fmt.Println("Abser nil", a)
	a = v
	fmt.Println("Abser", a)
	describe(a)

	// The opposite here, Scale is implemented by *Vertex
	// there is no explicit declaration that *Vertex implements Scaler
	// it compiles, and you are happy
	var s Scaler = &v
	fmt.Println("Scaler", s)
	// and you can call the method implemented
	s.Scale(0.2)
	fmt.Println("Scaler", s)
	describe(s)

	// An interface value holds a value of a specific underlying concrete type.
	// Calling a method on an interface value executes the method of the same
	// name on its underlying type.

	// https://tour.golang.org/methods/12
	// Interface values with nil underlying values are allowed
	var ns Scaler
	var nv *Vertex
	ns = nv
	describe(ns)
	// the method is called with a nil receiver
	// nil pointer is gracefully handled inside Scale
	ns.Scale(2)

	// Nil interface values:
	// A nil interface value holds neither value nor concrete type.
	// Calling a method on a nil interface is a run-time error because there is
	// no type inside the interface tuple to indicate which concrete method to
	// call.
	var ni Scaler
	describe(ni)

	// https://tour.golang.org/methods/15
	// A type assertion provides access to an interface value's underlying
	// concrete value.
	// t := i.(T)
	// This statement asserts that the interface value i holds the concrete
	// type T and assigns the underlying T value to the variable t.
	// If i does not hold a T, the statement will trigger a panic.
	// To test whether an interface value holds a specific type, a type
	// assertion can return two values: the underlying value and a boolean
	// value that reports whether the assertion succeeded.
	// t, ok := i.(T)
	_, svok1 := ns.(*Vertex)
	fmt.Println("Is this Scaler a *Vertex?", svok1)

	var si interface{} = "string"
	_, svok2 := si.(float64)
	fmt.Println("Is this interface a float64?", svok2)

	// type switch
	typeSwitch(21)
	typeSwitch("hello")
	typeSwitch(Vertex{1, 2})

	// method string for interface Stringer
	fmt.Println("A Vertex", v)
	anip := IPAddr{123, 54, 2, 234}
	fmt.Println("An IP", anip)

	anip, err := anip.FakeSetFirst(300)
	if err != nil {
		fmt.Println("Errored:", err)
	}

	_, err = ArtisanalSqrtErrored(-2)
	if err != nil {
		fmt.Println("Errored:", err)
	}

	// https://tour.golang.org/methods/21
	// The io.Reader interface has a Read method:
	// func (T) Read(b []byte) (n int, err error)
	// Read populates the given byte slice with data and returns the number of
	// bytes populated and an error value. It returns an io.EOF error when the
	// stream ends.
	r := strings.NewReader("Hello, Reader!  AZaz")

	b := make([]byte, 8)
	for {
		n, err := r.Read(b)
		fmt.Printf("n = %v err = %v b = %v\n", n, err, b)
		fmt.Printf("    b[:n] = %q\n", b[:n])
		if err == io.EOF {
			break
		}
	}

	snr := strings.NewReader("Lbh penpxrq gur pbqr!")
	rr := rot13Reader{snr}
	// br := make([]byte, 8)
	// for {
	// 	n, err := rr.Read(br)
	// 	// fmt.Printf("Read from rot13Reader n = %v err = %v br = %v\n", n, err, br)
	// 	fmt.Printf("    br[:n] = %q\n", br[:n])
	// 	if err == io.EOF {
	// 		break
	// 	}
	// }
	io.Copy(os.Stdout, &rr)
	fmt.Println("")

	// works in the magic tour
	m := Image{256, 256}
	// _ = Image{256, 256}
	// pic.ShowImage(m)

	// https://www.devdungeon.com/content/working-images-go

	// outputFile is a File type which satisfies Writer interface
	outputFile, err := os.Create("test.png")
	if err != nil {
		panic(err)
	}
	// Don't forget to close files
	defer outputFile.Close()

	// Encode takes a writer interface and an image interface
	// We pass it the File and the RGBA
	png.Encode(outputFile, m)
}
