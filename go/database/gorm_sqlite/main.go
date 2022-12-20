package main

import (
	"fmt"
	"log"
	"os"
	"time"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

type ProductWithModel struct {
	gorm.Model
	Code  string
	Price uint
}

// https://gorm.io/docs/index.html#Quick-Start
func minimal_with_model() {

	// create a logger
	newLogger := logger.New(
		log.New(os.Stdout, "\r\n", log.LstdFlags), // io writer
		logger.Config{
			SlowThreshold:             time.Second, // Slow SQL threshold
			LogLevel:                  logger.Info, // Log level
			IgnoreRecordNotFoundError: false,       // Show ErrRecordNotFound error for logger
			Colorful:                  true,        // Enable color
		},
	)

	db, err := gorm.Open(sqlite.Open("test_with_model.db"), &gorm.Config{
		Logger: newLogger,
	})
	if err != nil {
		// Failed to connect database
		panic(err)
	}

	// Migrate the schema
	db.AutoMigrate(&ProductWithModel{})

	// Create
	newProdId := db.Create(&ProductWithModel{Code: "D42", Price: 100})
	fmt.Printf("Created %+v\n", newProdId)

	newProd := &ProductWithModel{Code: "D42", Price: 100}
	db.Create(newProd)
	fmt.Printf("Created %+v\n", newProd)

	// Read
	var product ProductWithModel
	db.First(&product, 1) // find product with integer primary key

	// the following call produces
	// 	   SELECT * FROM `product_with_models`
	// 	   WHERE code = "D42"
	// 	   AND `product_with_models`.`deleted_at` IS NULL
	// 	   AND `product_with_models`.`id` = 1
	// 	   ORDER BY `product_with_models`.`id`
	// 	   LIMIT 1
	// because after the previous call product.ID is set
	// if you override it with product.ID = 1111 the following fails
	db.First(&product, "code = ?", "D42") // find product with code D42

	// Update - update product's price to 200
	db.Model(&product).Update("Price", 200)
	// Update - update multiple fields
	db.Model(&product).Updates(ProductWithModel{Price: 200, Code: "F42"}) // non-zero fields
	db.Model(&product).Updates(map[string]interface{}{"Price": 200, "Code": "F42"})

	// Delete - delete product
	db.Delete(&product, 1)
}

type ProductWithoutModel struct {
	Code  string `gorm:"primarykey"`
	Price uint
}

type UserWithoutModel struct {
	Name string `gorm:"primarykey"`
	Age  uint
}

// Without model in the struct.
//
// https://gorm.io/docs/index.html#Quick-Start
// https://gorm.io/docs/advanced_query.html#FirstOrCreate
// https://gorm.io/docs/query.html#Retrieving-all-objects
func minimal_without_model() {

	dbPath := "test_without_model.db"
	os.Remove(dbPath)

	// create a logger
	newLogger := logger.New(
		log.New(os.Stdout, "\r\n", log.LstdFlags), // io writer
		logger.Config{
			SlowThreshold:             time.Second, // Slow SQL threshold
			LogLevel:                  logger.Info, // Log level
			IgnoreRecordNotFoundError: false,       // Show ErrRecordNotFound error for logger
			Colorful:                  true,        // Enable color
		},
	)

	db, err := gorm.Open(sqlite.Open(dbPath), &gorm.Config{
		Logger: newLogger,
	})
	if err != nil {
		// Failed to connect database
		panic(err)
	}

	// Migrate the schema
	db.AutoMigrate(&ProductWithoutModel{})
	db.AutoMigrate(&UserWithoutModel{})

	// Create
	newProd := &ProductWithoutModel{Code: "D42", Price: 100}
	db.Create(newProd)
	fmt.Printf("Created %+v\n", newProd)

	// Create on another table
	newUser := &UserWithoutModel{Name: "Pippo", Age: 51}
	db.Create(newUser)
	fmt.Printf("Created %+v\n", newUser)

	// Read
	var product ProductWithoutModel
	db.First(&product, "D42")             // find product with primary key who knows
	db.First(&product, "code = ?", "D42") // find product with code D42

	// Update - update product's price to 200
	db.Model(&product).Update("Price", 200)
	// Update - update multiple fields
	db.Model(&product).Updates(ProductWithoutModel{Price: 200, Code: "F42"}) // non-zero fields
	db.Model(&product).Updates(map[string]interface{}{"Price": 200, "Code": "F42"})

	// Delete - delete product
	// db.Delete(&product, "F42") // invalid column
	db.Delete(&product)
	db.Delete(&product, "code = ?", "F42")

	// Update a non existing product?
	nonExistingProd := ProductWithoutModel{Price: 200, Code: "New41"}
	db.Model(&nonExistingProd).Updates(nonExistingProd) // non-zero fields
	// fails obviously

	// FirstOrCreate
	result := db.FirstOrCreate(&nonExistingProd, nonExistingProd)
	fmt.Printf("Rows Affected %d\n", result.RowsAffected)

	// Create then update
	updateProd := &ProductWithoutModel{Code: "New45", Price: 100}
	db.Create(updateProd)
	fmt.Printf("Created %+v\n", updateProd)
	db.Model(&ProductWithoutModel{Code: "New45"}).Update("Price", 205)

	// Get all records
	var allProducts []ProductWithoutModel

	// SELECT * FROM blah;
	result = db.Find(&allProducts)
	// returns found records count, equals `len(allProducts)`
	fmt.Printf("RowsAffected %+v\n", result.RowsAffected)
	// result.Error // returns error

	// SELECT * WHERE equal
	result = db.Find(&allProducts, &ProductWithoutModel{Code: "New45"})
	fmt.Printf("RowsAffected %+v\n", result.RowsAffected)

	// SELECT * FROM blah WHERE code = 'New45' AND price >= 50;
	result = db.Where("code = ? AND price >= ?", "New45", "50").Find(&allProducts)
	fmt.Printf("RowsAffected %+v\n", result.RowsAffected)
}

// https://gorm.io/docs/create.html#Batch-Insert
func batch() {

	var products = []ProductWithModel{
		{Code: "P1", Price: 100},
		{Code: "P2", Price: 150},
		{Code: "P3", Price: 160},
	}

	// create a logger
	newLogger := logger.New(
		log.New(os.Stdout, "\r\n", log.LstdFlags), // io writer
		logger.Config{
			SlowThreshold:             time.Second, // Slow SQL threshold
			LogLevel:                  logger.Info, // Log level
			IgnoreRecordNotFoundError: false,       // Show ErrRecordNotFound error for logger
			Colorful:                  true,        // Enable color
		},
	)

	db, err := gorm.Open(sqlite.Open("test_with_model.db"), &gorm.Config{
		Logger: newLogger,
	})
	if err != nil {
		// Failed to connect database
		panic(err)
	}

	// create all the products
	db.Create(&products)

	// as we have the ID as primary key, that filed will be set
	// for _, prod := range products {
	// 	prod.ID // 1,2,3
	// }

}

func main() {

	// which := "minimal_with_model"
	which := "minimal_without_model"
	// which := "batch"
	fmt.Printf("which = %s\n", which)

	switch which {
	case "minimal_with_model":
		minimal_with_model()
	case "minimal_without_model":
		minimal_without_model()
	case "batch":
		batch()
	}

}
