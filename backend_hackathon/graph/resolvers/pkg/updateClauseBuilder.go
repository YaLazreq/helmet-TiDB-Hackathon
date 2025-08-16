package resolvers

import (

	"github.com/iancoleman/strcase"
	"reflect"
	"strings"

	"fmt"
)

func UpdateClauseBuilder(filter any) string {

	filter_fields := extractFilterStructFields(filter)

	updateClause := ""

	var idx int = 1

	if filter != nil {
		for i := range filter_fields {
			field := filter_fields[i]
			value := reflect.ValueOf(filter).Elem().FieldByName(field)
			clause := ""

			if value.IsValid() && value.Kind() == reflect.Ptr {
				if !value.IsNil() {
					clause = fmt.Sprintf("%s = ?%d", strcase.ToSnake(field), idx)
					idx++
				}
			}

			if clause != "" {
				updateClause += clause + ", "
			}
		}
	}

	updateClause = strings.TrimSuffix(updateClause, ", ")

	if updateClause != "" {
		updateClause = " SET " + updateClause
	}

	return updateClause
}
