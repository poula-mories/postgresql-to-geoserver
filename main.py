import json
import psycopg2
import requests

# Function to read parameters from JSON configuration file
def read_config(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

# Function to connect to the PostgreSQL database
def connect_to_postgres(host, port, user, password, dbname):
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        dbname=dbname,
        port=port
    )
    return conn


# Function to get a list of tables/views from the specified schema
def get_tables(conn, schema):
    tables = []
    cursor = conn.cursor()
    cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'")
    tables.extend(cursor.fetchall())
    cursor.close()
    return tables


# Function to check if workspace exists in GeoServer
def workspace_exists(host, port, user, password, workspace):
    url = f"http://{host}:{port}/geoserver/rest/workspaces/{workspace}"
    response = requests.get(url, auth=(user, password))
    return response.status_code == 200

# Function to create workspace in GeoServer
def create_workspace(host, port, user, password, workspace):
    url = f"http://{host}:{port}/geoserver/rest/workspaces"
    headers = {'Content-Type': 'application/xml'}
    data = f"<workspace><name>{workspace}</name></workspace>"
    response = requests.post(url, data=data, headers=headers, auth=(user, password))
    print(response)
    return response.status_code == 201

# Function to check if store exists in GeoServer
def store_exists(host, port, user, password, workspace, store_name):
    url = f"http://{host}:{port}/geoserver/rest/workspaces/{workspace}/datastores/{store_name}"
    response = requests.get(url, auth=(user, password))
    return response.status_code == 200

# Function to create store in GeoServer
def create_store(host, port, user, password, workspace, store_name, dbhost, dbname, dbuser, dbpass, dbport):
    url = f"http://{host}:{port}/geoserver/rest/workspaces/{workspace}/datastores"
    headers = {'Content-Type': 'application/xml'}
    data = f"<dataStore><name>{store_name}</name><connectionParameters><host>{dbhost}</host><port>{dbport}</port><database>{dbname}</database><schema>{store_name}</schema><user>{dbuser}</user><passwd>{dbpass}</passwd><dbtype>postgis</dbtype></connectionParameters></dataStore>"
    response = requests.post(url, data=data, headers=headers, auth=(user, password))
    return response.status_code == 201

# Function to publish layers to GeoServer
def publish_to_geoserver(host, port, user, password, workspace, datastore, table_name):
    url = f"http://{host}:{port}/geoserver/rest/workspaces/{workspace}/datastores/{datastore}/featuretypes"
    headers = {'Content-Type': 'application/json'}
    auth = (user, password)
    data = {
        "featureType": {
            "name": table_name,
            "nativeName": table_name,
            "title": table_name,
            "enabled": True
        }
    }
    

    response = requests.post(url, json=data, headers=headers, auth=auth)
    if response.status_code == 201:
        print(f"Layer '{table_name}' published successfully to GeoServer.")
    else:
        print(f"Failed to publish layer '{table_name}' to GeoServer. Error: {response.text}")

# Main function
def main():
    # Read parameters from configuration file
    config = read_config('config.json')
    postgresql_config = config['postgresql']
    geoserver_config = config['geoserver']
    schemas = config['schemas']
    workspace = postgresql_config['dbname']  # Workspace name is set to dbname
    
    # Connect to PostgreSQL
    conn = connect_to_postgres(**postgresql_config)
    
    if conn:
        print("DB connected successfully")
    else:
        print("Can't connect to DB")
        return
    
    # Check if workspace exists, if not, create it
    if not workspace_exists(**geoserver_config, workspace=workspace):
        if create_workspace(**geoserver_config, workspace=workspace):
            print(f"Workspace '{workspace}' created successfully.")
        else:
            print(f"Failed to create workspace '{workspace}'.")
            return
    
    # Get tables/views from specified schema
    for schema in schemas:
        tables = get_tables(conn, schema)
    
    
    # Publish each table/view to GeoServer
        for table in tables:
            table_name = table[0]
            store_name = schema  # Store name is set to schema name
            # Check if store exists, if not, create it
            if not store_exists(**geoserver_config, workspace=workspace, store_name=store_name):
                if create_store(**geoserver_config, workspace=workspace, store_name=store_name,dbhost=postgresql_config['host'], dbname=postgresql_config['dbname'], dbuser=postgresql_config['user'] , dbpass=postgresql_config['password'], dbport=postgresql_config['port']):
                    print(f"Datastore '{store_name}' created successfully.")
                else:
                    print(f"Failed to create datastore '{store_name}'.")
                    continue
            
 
            # Publish layer to GeoServer
            publish_to_geoserver(**geoserver_config, workspace=workspace, datastore=store_name, table_name=table_name)
    
    # Close PostgreSQL connection
    conn.close()
    print("Script Finished")
if __name__ == "__main__":
    main()
