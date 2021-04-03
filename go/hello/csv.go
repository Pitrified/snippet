package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

// https://gobyexample.com/writing-files
// https://golang.org/pkg/encoding/csv/#Writer

func csvWriteString() {

	f, err := os.Create("sample_csv.csv")
	check(err)
	defer f.Close()

	records := [][]string{
		{"first_name", "last_name", "username"},
		{"Rob", "Pike", "rob"},
		{"Ken", "Thompson", "ken"},
		{"Robert", "Griesemer", "gri"},
	}

	w := csv.NewWriter(f)

	for _, record := range records {
		if err := w.Write(record); err != nil {
			log.Fatalln("error writing record to csv:", err)
		}
	}

	// Write any buffered data to the underlying writer (standard output).
	w.Flush()

	if err := w.Error(); err != nil {
		log.Fatal(err)
	}
}

// https://golang.org/pkg/encoding/csv/#Reader

func csvReadString() {
	f, err := os.Open("sample_csv.csv")
	check(err)
	defer f.Close()

	r := csv.NewReader(f)

	records, err := r.ReadAll()
	if err != nil {
		log.Fatal(err)
	}

	fmt.Print(records)

	// rewind the file
	f.Seek(0, 0)
	r = csv.NewReader(f)

	for {
		record, err := r.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("First name: %s Last name %s\n", record[0], record[1])
	}
}
