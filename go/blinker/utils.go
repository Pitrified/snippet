package main

import (
	"io/fs"
	"math/rand"
	"os"
	"time"
)

func randSleep(sec float64, ch chan<- string) {
	time.Sleep(time.Duration(rand.Float64() * 1e9 * sec))
	ch <- "Done."
}

func randDuration(begin float64, length float64) time.Duration {
	return time.Duration((begin + rand.Float64()*length) * 1e9)
}

func intAbs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// https://stackoverflow.com/a/56600630/2237151
func ensureDir(dirName string, mode fs.FileMode) error {
	err := os.Mkdir(dirName, mode)
	if err == nil || os.IsExist(err) {
		return nil
	} else {
		return err
	}
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}
