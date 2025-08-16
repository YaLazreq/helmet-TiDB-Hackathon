package resolvers

import (
	"backend_hackathon/graph/model"
	pkg "backend_hackathon/graph/resolvers/pkg"
	"fmt"
	"log"

	"github.com/jmoiron/sqlx"
)

func CreateUser(db *sqlx.DB, input *model.CreateUserInput) (int, error) {

	query := "INSERT INTO users"
	query += pkg.CreateFieldBuilder(input)

	values := pkg.ExtractFilterStructValues(input)

	log.Println("query:", query)
	log.Println("values:", values)

	res, err := db.Exec(query, values...)
	if err != nil {
		return -1, fmt.Errorf("insert user: %w", err)
	}

	lastID, err := res.LastInsertId()
	if err != nil {
		return -1, fmt.Errorf("get last insert id: %w", err)
	}

	return int(lastID), nil
}
