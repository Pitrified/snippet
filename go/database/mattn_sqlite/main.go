package main

import (
	"database/sql"
	"fmt"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type User struct {
	UserId     int
	Username   string
	Department string
	Created    time.Time
}

// Sample use of the sqlite library.
//
// https://astaxie.gitbooks.io/build-web-application-with-golang/content/en/05.3.html
func main() {
	db, err := sql.Open("sqlite3", "./foo.db")
	checkErr(err)

	createStr := `CREATE TABLE IF NOT EXISTS userinfo (
        uid INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(64) NULL,
        department_name VARCHAR(64) NULL,
        created DATE NULL
    );`
	stmt, err := db.Prepare(createStr)
	checkErr(err)
	res, err := stmt.Exec()
	checkErr(err)
	checkAffected(res)
	checkInsertId(res)
	// you should actually always close the statement when you are done
	err = stmt.Close()
	checkErr(err)

	// insert
	stmt, err = db.Prepare("INSERT INTO userinfo(username, department_name, created) values(?,?,?)")
	checkErr(err)

	// res, err = stmt.Exec("my_name", "my_department", "2012-12-09")
	today := time.Now()
	res, err = stmt.Exec("my_name", "my_department", today)
	checkErr(err)
	id := checkInsertId(res)

	// update
	stmt, err = db.Prepare("update userinfo set username=? where uid=?")
	checkErr(err)

	res, err = stmt.Exec("my_name_update", id)
	checkErr(err)
	checkAffected(res)

	// query
	rows, err := db.Query("SELECT * FROM userinfo")
	checkErr(err)
	user := User{}

	for rows.Next() {
		err = rows.Scan(
			&user.UserId,
			&user.Username,
			&user.Department,
			&user.Created,
		)
		checkErr(err)
		fmt.Printf("%+v\n", user)
		// fmt.Println(user.UserId)
		// fmt.Println(user.Username)
		// fmt.Println(user.Department)
		// fmt.Println(user.Created)
	}

	rows.Close() //good habit to close

	// // delete
	// stmt, err = db.Prepare("delete from userinfo where uid=?")
	// checkErr(err)
	// res, err = stmt.Exec(id)
	// checkErr(err)
	// checkAffected(res)

	db.Close()
}

func checkInsertId(res sql.Result) int64 {
	id, err := res.LastInsertId()
	checkErr(err)
	fmt.Println(id)
	return id
}

func checkAffected(res sql.Result) {
	affect, err := res.RowsAffected()
	checkErr(err)
	fmt.Println(affect)
}

func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}
