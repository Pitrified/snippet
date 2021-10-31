# Organizing Go code

[Organizing Go code](https://go.dev/blog/organizing-go-code)

`go.mod`

```go
module modulename

go 1.16
```

`main.go`

```go
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
```

`foldername1/filename1.go`

```go
package packagename1

import "fmt"

func ExportedFn1() {
	fmt.Println("This has been exported, and can be used as packagename1.ExportedFn1().")
	notExportedFn1()
}

func notExportedFn1() {
	fmt.Println("This has not been exported, but can be called from within the package packagename1.")
}
```

`foldername2/subfoldername2/filename2.go`

```go
package packagename2sub

import (
	"fmt"
	packagename1 "modulename/foldername1"
)

func ExportedFnSub2() {
	fmt.Println("Exported from packagename2 subfolder.")
	packagename1.ExportedFn1()
}
```
