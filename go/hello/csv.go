package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
	"time"
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

	// Write any buffered data to the underlying writer.
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
		} else if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("First name: %s Last name %s\n", record[0], record[1])
	}
}

type Person struct {
	name        string
	age         int
	height      float64
	dateOfBirth time.Time
}

func (p *Person) ToSlice() []string {
	record := make([]string, 4)
	record[0] = p.name
	record[1] = fmt.Sprintf("%v", p.age)
	record[2] = fmt.Sprintf("%v", p.height)
	record[3] = fmt.Sprintf("%v", p.dateOfBirth)
	return record
}

func (p *Person) String() string {
	return fmt.Sprintf("Name: %v Age %v Height %v Date %v",
		p.name, p.age, p.height, p.dateOfBirth)
}

func NewPerson(record []string) *Person {
	name := record[0]
	age, err := strconv.Atoi(record[1])
	check(err)
	height, err := strconv.ParseFloat(record[2], 64)
	check(err)
	layout := "2006-01-02 15:04:05.999999999 -0700 MST"
	dateOfBirth, err := time.Parse(layout, record[3])
	check(err)
	return &Person{name, age, height, dateOfBirth}
}

func csvWriteStruct() {

	records := make([]Person, 3)
	records[0] = Person{"Alice", 24, 1.64, time.Date(2009, time.November, 10, 23, 0, 0, 0, time.UTC)}
	records[1] = Person{"Bob", 25, 1.79, time.Date(2010, time.November, 10, 23, 0, 0, 0, time.UTC)}
	records[2] = Person{"Charlie", 23, 1.78, time.Date(2011, time.November, 10, 23, 0, 0, 0, time.UTC)}

	f, err := os.Create("sample_csv_person.csv")
	check(err)
	defer f.Close()

	w := csv.NewWriter(f)

	for _, record := range records {
		if err := w.Write(record.ToSlice()); err != nil {
			log.Fatalln("error writing record to csv:", err)
		}
	}

	// Write any buffered data to the underlying writer.
	w.Flush()

	if err := w.Error(); err != nil {
		log.Fatal(err)
	}
}

func csvReadStruct() {

	f, err := os.Open("sample_csv_person.csv")
	check(err)
	defer f.Close()

	r := csv.NewReader(f)

	var persons []Person

	for {
		record, err := r.Read()
		if err == io.EOF {
			break
		} else if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("Name: %s Age %s Height %s Date %s\n",
			record[0], record[1], record[2], record[3])

		persons = append(persons, *NewPerson(record))
	}

	for _, person := range persons {
		fmt.Printf("person = %v\n", &person)
	}

}
