package resolvers

import (
	"backend_hackathon/graph/model"
	pkg "backend_hackathon/graph/resolvers/pkg"

	"github.com/jmoiron/sqlx"
)

func UpdateUser(db *sqlx.DB, input *model.UpdateUserInput, filter *model.CreateUserInput) (bool, error) {
	query := "UPDATE users"

	query += pkg.UpdateClauseBuilder(input)
	values_update := pkg.ExtractFilterStructValues(input)

	query += pkg.WhereClauseBuilder(filter)
	values_where := pkg.ExtractFilterStructValues(filter)

	values := append(values_update, values_where...)

	db.Exec(query, values...)

	return true, nil
}
