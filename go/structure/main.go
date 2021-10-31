package main

import (
	"fmt"

	// this is bad practice: use the same folder and package name
	// so you can just import "modulename/foldername1"
	// I just wanted to understand what each element was
	packagename1 "modulename/foldername1"
	packagename2sub "modulename/foldername2/subfoldername2"
)

func main() {
	fmt.Println("vim-go")
	packagename1.ExportedFn1()
	packagename2sub.ExportedFnSub2()
}
