# postgresql-to-geoserver
This script facilitates the process of publishing data from PostgreSQL databases to GeoServer. It automates the creation of workspaces, stores, and layers in GeoServer based on the specified configurations.

## Prerequisites
Before running this script, ensure you have the following:

* Python 3.x installed
* Required Python libraries installed (psycopg2, requests)
* Access to a PostgreSQL database
* Access to GeoServer

# Installation
Clone this repository to your local machine:

```bash
git clone https://github.com/your_username/postgresql-to-geoserver.git
```

Navigate to the project directory:

```bash
cd postgresql-to-geoserver
Install the required Python libraries:
```

```bash
pip install -r requirements.txt
```

## Usage
1.Ensure your PostgreSQL database is running and accessible.

2.Configure the config.json file according to your environment. Here's an example configuration:
```json
{
    "postgresql": {
        "host": "localhost",
        "user": "postgres",
        "port": 5432,
        "password": "postgres",
        "dbname": "olympic"
    },
    "schemas": ["cctv", "bms"],
    "geoserver": {
        "host": "localhost",
        "port": 8080,
        "user": "admin",
        "password": "geoserver"
    }
}
```
3. Run the script:

```bash
python main.py
```

## Configuration Explanation
PostgreSQL: Details required to connect to your PostgreSQL database.
Schemas: List of schemas containing tables/views to be published.
GeoServer: Details required to connect to your GeoServer instance.

## Script Functionality
Connects to PostgreSQL database.
Checks for the existence of the workspace in GeoServer; creates it if it doesn't exist.
Retrieves tables/views from specified schemas in the PostgreSQL database.
Creates stores in GeoServer corresponding to the schemas.
Publishes layers to GeoServer.

## Note
Ensure that GeoServer is running and accessible before running this script.
Make sure that GeoServer's REST API is enabled and accessible.

