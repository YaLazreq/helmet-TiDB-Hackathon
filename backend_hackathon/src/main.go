package main

import (
	"log"
	"net/http"
	"os"

	"github.com/99designs/gqlgen/graphql/handler"
	"github.com/99designs/gqlgen/graphql/playground"

	"backend_hackathon/graph"
	"backend_hackathon/graph/generated"
	db_pckg "backend_hackathon/src/db"
)

func main() {

	port := os.Getenv("APP_PORT")

	db, err := db_pckg.Connect()
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	srv := handler.NewDefaultServer(generated.NewExecutableSchema(
		generated.Config{Resolvers: &graph.Resolver{DB : db}},
	))
	

	http.Handle("/", playground.Handler("GraphQL playground", "/query"))
	http.Handle("/query", srv)

	log.Println("Server running at http://localhost:"+port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
