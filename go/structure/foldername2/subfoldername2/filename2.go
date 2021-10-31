package packagename2sub

import (
	"fmt"
	packagename1 "modulename/foldername1"
)

func ExportedFnSub2() {
	fmt.Println("Exported from packagename2 subfolder.")
	packagename1.ExportedFn1()
}
