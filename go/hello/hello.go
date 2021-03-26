package main

import (
	"encoding/json"
	"fmt"
	"strings"
	"testing"
)

type Foo struct {
	Name    string
	Ports   []int
	Enabled bool
}

type foo struct {
	Message    string
	Ports      []int
	ServerName string
}

func newFoo() (*foo, error) {
	return &foo{
		Message:    "foo loves bar",
		Ports:      []int{80},
		ServerName: "Foo",
	}, nil
}

func countLines(msg string) int {
	var count int
	for i := 0; i < len(msg); i++ {
		if msg[i] == '\n' {
			count++
		}
	}
	return count
}

func main() {
	fmt.Println("vim-go saved")
	fmt.Println(strings.ToUpper("gopher"))

	foo := Foo{Name: "gopher", Ports: []int{80, 443}, Enabled: true}
	fmt.Printf("string(foo.Name) = %+v\n", string(foo.Name))

	res, err := newFoo()
	if err != nil {
		panic(err)
	}

	out, err := json.Marshal(res)
	if err != nil {
		panic(err)
	}

	fmt.Printf("string(out) = %+v\n", string(out))

	msg := "Greetings\nfrom\nItaly."
	count := countLines(msg)
	fmt.Printf("count = %+v\n", count)

	tourBasic()
	tourFlow()
	tourTypes()
	tourMethods()

	effectiveConstant()
	effectiveInit()
	effectiveBlank()
	effectiveChannels()
}

func TestBar(t *testing.T) {
	result := Bar()
	if result != "bar" {
		t.Errorf("expecting bar, got %s", result)
	}
}
