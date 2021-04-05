package main

import (
	"container/list"
	"fmt"
)

func sampleList() {
	// Create a new list and put some numbers in it.
	l := list.New()
	fmt.Printf("l = %+v\n", l)
	e4 := l.PushBack(4)
	e1 := l.PushFront(1)
	l.InsertBefore(3, e4)
	l.InsertAfter(2, e1)
	fmt.Printf("l = %+v\n", l)

	// Iterate through list and print its contents.
	for e := l.Front(); e != nil; e = e.Next() {
		fmt.Println(e.Value)
	}
}
