package resolvers

import (

	"github.com/iancoleman/strcase"
	"strings"

	"fmt"
)

func CreateFieldBuilder(filter any) string {

	filter_fields := extractFilterStructFields(filter)

	createField := ""

	if filter != nil {
		for i := range filter_fields {
			field := filter_fields[i]

			createField += fmt.Sprintf("%s, ", strcase.ToSnake(field))

			}

			createField = strings.TrimSuffix(createField, ", ")

		}

	if createField != "" {
		createField = " (" + createField + ")"

		createField += " VALUES ("
		for _ = range filter_fields {

			createField += "?, "

		}
	}
	
	createField = strings.TrimSuffix(createField, ", ")
	createField += ")"

	return createField
}
