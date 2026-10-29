
import os
import psycopg2
import streamlit as st


def get_connection():
    """Connect to PostgreSQL using environment variables or Streamlit secrets."""
    try:
        config = {}

        try:
            config = dict(st.secrets.get("postgres", {}))
        except Exception:
            pass

        host = os.getenv("PGHOST") or config.get("host")
        port = os.getenv("PGPORT") or config.get("port", "5432")
        database = os.getenv("PGDATABASE") or config.get("database")
        user = os.getenv("PGUSER") or config.get("user")
        password = os.getenv("PGPASSWORD") or config.get("password")

        if not all([host, database, user, password]):
            raise ValueError(
                "Database settings are missing. Configure an online "
                "PostgreSQL database in Streamlit Cloud Secrets."
            )

        sslmode = os.getenv("PGSSLMODE") or config.get("sslmode")
        if not sslmode:
            sslmode = "prefer" if host in ("localhost", "127.0.0.1") else "require"

        connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password,
            connect_timeout=10,
            sslmode=sslmode,
        )
        return connection

    except Exception as error:
        print(f"PostgreSQL connection error: {error}")
        raise RuntimeError(
            "Could not connect to PostgreSQL. Check the database host, "
            "database name, username, password, and network access."
        ) from error
