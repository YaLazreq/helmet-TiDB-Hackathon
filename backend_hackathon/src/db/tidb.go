package db

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"os"

	_ "github.com/go-sql-driver/mysql"
	"github.com/go-sql-driver/mysql"
	"github.com/jmoiron/sqlx"
)

var DB *sqlx.DB

func Connect() (*sqlx.DB, error) {
	host := os.Getenv("DB_HOST")
	port := os.Getenv("DB_PORT")
	user := os.Getenv("DB_USER")
	password := os.Getenv("DB_PASSWORD")
	dbname := os.Getenv("DB_NAME")
	caPath := os.Getenv("DB_SSL_CA")

	rootCAs := x509.NewCertPool()
	pem, err := os.ReadFile(caPath)
	if err != nil {
		return nil, fmt.Errorf("read CA file: %w", err)
	}
	if !rootCAs.AppendCertsFromPEM(pem) {
		return nil, fmt.Errorf("failed to append CA")
	}

	err = mysql.RegisterTLSConfig("tidb", &tls.Config{
		RootCAs: rootCAs,
	})
	if err != nil {
		return nil, fmt.Errorf("register TLS: %w", err)
	}

	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?parseTime=true&tls=tidb",
		user, password, host, port, dbname,
	)

	DB, err = sqlx.Connect("mysql", dsn)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	return DB, nil
}
