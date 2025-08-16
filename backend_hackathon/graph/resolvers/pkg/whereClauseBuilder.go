package resolvers

import (
	
	"github.com/iancoleman/strcase"
	"reflect"
	"strings"

	"fmt"
)

func WhereClauseBuilder(filter any) string {

	filter_fields := extractFilterStructFields(filter)

	whereClause := ""

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
				whereClause += clause + " AND "
			}
		}
	}

	whereClause = strings.TrimSuffix(whereClause, " AND ")

	if whereClause != "" {
		whereClause = " WHERE " + whereClause
	}

	return whereClause
}
