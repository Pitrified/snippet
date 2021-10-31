package packagename1

import "fmt"

func ExportedFn1() {
	fmt.Println("This has been exported, and can be used as packagename1.ExportedFn1().")
	notExportedFn1()
}

func notExportedFn1() {
	fmt.Println("This has not been exported, but can be called from within the package packagename1.")
}
