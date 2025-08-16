package resolvers

import (
	"backend_hackathon/graph/model"
	pkg "backend_hackathon/graph/resolvers/pkg"
	"log"

	"github.com/jmoiron/sqlx"

	"context"

	"fmt"
	"strings"
)

func GetUsers(ctx context.Context, db *sqlx.DB, filter *model.UserFilter) ([]*model.User, error) {

	var users []*model.User

	whereClause := pkg.WhereClauseBuilder(filter)

	field := pkg.ExtractFields(ctx)
	values := pkg.ExtractFilterStructValues(filter)

	// log.Println("field", field)
	log.Println("whereClause", whereClause)

	query := fmt.Sprintf("SELECT %s FROM users%s", strings.Join(field, ", "), whereClause)

	log.Println("query", query)
	log.Println("values", values)

	var err error = nil

	if strings.TrimSpace(whereClause) == "" {
    err = db.Select(&users, query) // pas d’args
	} else {
		err = db.Select(&users, query, values...) // args seulement si WHERE
	}

	if err != nil {
		log.Println("Error executing query:", err)
		return nil, err
	}

	return users, nil
}
