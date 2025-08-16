package resolvers

import (
	"context"

	"github.com/99designs/gqlgen/graphql"

	"reflect"
)

func ExtractFields(ctx context.Context) []string {
	raw_fields := graphql.CollectFieldsCtx(ctx, nil)
	fields := []string{}
	for _, f := range raw_fields {
		fields = append(fields, f.Name)
	}
	
	return fields
}

func extractFilterStructFields(filter any) []string {
	val := reflect.ValueOf(filter)
	if val.Kind() == reflect.Ptr {
		val = val.Elem()
	}

	typ := val.Type()

	filter_field := []string{}

	for i := 0; i < typ.NumField(); i++ {
		field := typ.Field(i)
		filter_field = append(filter_field, field.Name)
	}

	return filter_field
}

func ExtractFilterStructValues(filter any) []any {
	val := reflect.ValueOf(filter)
	if val.Kind() == reflect.Ptr {
		val = val.Elem()
	}

	typ := val.Type()

	filter_field := []any{}

	for i := 0; i < typ.NumField(); i++ {
		value := val.Field(i).Interface()
		filter_field = append(filter_field, value)
	}

	return filter_field
}
