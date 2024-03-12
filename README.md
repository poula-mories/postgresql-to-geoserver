# postgresql-to-geoserver
This script facilitates the process of publishing data from PostgreSQL databases to GeoServer. It automates the creation of workspaces, stores, and layers in GeoServer based on the specified configurations.

## Prerequisites
Before running this script, ensure you have the following:

* Python 3.x installed
* Required Python libraries installed (psycopg2, requests, paramiko)
* Access to a PostgreSQL database
* Access to GeoServer

# Installation
Clone this repository to your local machine:

```bash
git clone https://github.com/poula-mories/postgresql-to-geoserver.git
```

Navigate to the project directory:

```bash
cd postgresql-to-geoserver
```

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

## Usage
1.Ensure your PostgreSQL database is running and accessible.

2.Configure the config.json file according to your environment. Here's an example configuration:
```json
{
    "postgresql": {
        "host": "DB_host",
        "user": "DB_user",
        "port":5432,
        "password": "DB_pass",
        "dbname": "DB_name"
    },
    "ssh": {
        "enable_ssh": true,
        "ssh_host": "SSH_host",
        "ssh_user": "SSH_user",
        "ssh_password": "SSH_password",
        "ssh_pem_key": "path/to/your/pem/key.pem",
        "ssh_port": 22
    },
    "schemas": ["schema1", "schema2"],
    "geoserver": {
        "url":"http://GEOSERVER_host:8080",
        "user": "GEOSERVER_user",
        "password": "GEOSERVER_pass"
    }
}

```
3. Run the script:

```bash
python main.py
```

## Configuration Explanation
* PostgreSQL: Details required to connect to your PostgreSQL database.
* ssh: SSH tunnel configuration to connect to the Server.
* Schemas: List of schemas containing tables/views to be published.
* GeoServer: Details required to connect to your GeoServer instance.

## Script Functionality
Connects to PostgreSQL database directly or via SSH tunnel.
Checks for the workspace in GeoServer; creates it if it doesn't exist.
Retrieves tables/views from specified schemas in the PostgreSQL database.
Creates stores in GeoServer corresponding to the schemas.
Publishes layers to GeoServer.

## Note
Ensure that GeoServer is running and accessible before running this script.
Make sure that GeoServer's REST API is enabled and accessible.
If connecting to PostgreSQL via SSH tunnel, provide either ssh_password or ssh_pem_key in the config.json.
