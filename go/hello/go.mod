module example.com/hello

go 1.16

require (
	example.com/turtle v0.0.0-00010101000000-000000000000
	golang.org/x/tour v0.0.0-20210317163553-0a3a62c5e5c0
)

replace example.com/turtle => ../turtle
