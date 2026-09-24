import os
import yaml
import arcpy
import logging

# ---------- CONFIG ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASES_DIR = os.path.join(BASE_DIR, "Databases")
DB_YAML_PATH = os.path.join(BASE_DIR, "config.yaml")

# ---------- LOGGING ----------
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO in production
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ---------- INSTANCE TYPE ----------
def get_database_platform(instance_type):
    normalized = instance_type.strip().lower()

    mapping = {
        "sql server": "SQL_SERVER",
        "oracle": "ORACLE",
        "postgresql": "POSTGRESQL"
    }

    if normalized not in mapping:
        raise ValueError(f"Unsupported instance_type: {instance_type}")

    return mapping[normalized]


# ---------- ROOT ----------
def ensure_databases_root():
    if not os.path.exists(DATABASES_DIR):
        os.makedirs(DATABASES_DIR)
        logging.info(f"Created parent Databases folder: {DATABASES_DIR}")
    else:
        logging.info(f"Databases folder already exists: {DATABASES_DIR}")


# ---------- FOLDER ----------
def create_folder_structure(db_name):
    db_path = os.path.join(DATABASES_DIR, db_name)
    dataowners_path = os.path.join(db_path, "DataOwners")
    admin_path = os.path.join(db_path, "Admin")

    os.makedirs(dataowners_path, exist_ok=True)
    os.makedirs(admin_path, exist_ok=True)

    return db_path, dataowners_path, admin_path


# ---------- CONNECTION ----------
def create_sde_connection(out_folder, connection_name, db_platform, instance, database, username, password):
    out_path = os.path.join(out_folder, connection_name)

    if os.path.exists(out_path):
        logging.info(f"Connection already exists: {out_path}")
        return

    try:
        arcpy.management.CreateDatabaseConnection(
            out_folder_path=out_folder,
            out_name=connection_name,
            database_platform=db_platform,
            instance=instance,
            account_authentication="DATABASE_AUTH",
            username=username,
            password=password,
            save_user_pass="SAVE_USERNAME",
            database=database
        )
        logging.info(f"Created connection: {out_path}")

    except Exception as e:
        logging.error(f"Failed to create connection {connection_name}: {str(e)}")


# ---------- MAIN ----------
def process_databases():
    with open(DB_YAML_PATH, "r") as f:
        config = yaml.safe_load(f)

    # ---------- GLOBAL VALUES ----------
    instance = config["instance"].strip()
    instance_type = config["instance_type"].strip()
    admin_user = config["admin_user"].strip()
    admin_pwd = config["admin_password"].strip()

    db_platform = get_database_platform(instance_type)

    sde_user = config.get("sde_user", "").strip() or None
    sde_pwd = config.get("sde_password", "").strip() or None

    logging.info(f"Using instance: {instance}")
    logging.info(f"Using instance_type: {instance_type}")
    logging.info(f"Using admin_user: {admin_user}")

    # ---------- LOOP DATABASES ----------
    for db_entry in config.get("databases", []):
        database = db_entry.get("name", "").strip()

        if not database:
            continue

        data_owner = db_entry.get("data_owner", "").strip() or None
        data_owner_pwd = db_entry.get("data_owner_password", "").strip() or None

        logging.info(f"Processing database: {database}")

        db_path, dataowners_path, admin_path = create_folder_structure(database)

        # ---------- ADMIN ----------
        create_sde_connection(
            admin_path,
            "admin_connection.sde",
            db_platform,
            instance,
            database,
            admin_user,
            admin_pwd
        )

        # ---------- DATA OWNER ----------
        if data_owner and data_owner_pwd:
            dataowner_conn_name = f"{data_owner}_connection.sde"

            create_sde_connection(
                dataowners_path,
                dataowner_conn_name,
                db_platform,
                instance,
                database,
                data_owner,
                data_owner_pwd
            )
        else:
            logging.warning(f"Skipping data owner connection for {database} due to missing credentials")

        # ---------- SDE ----------
        if sde_user and sde_pwd:
            create_sde_connection(
                dataowners_path,
                "sde_connection.sde",
                db_platform,
                instance,
                database,
                sde_user,
                sde_pwd
            )


# ---------- ENTRY ----------
if __name__ == "__main__":
    ensure_databases_root()
    process_databases()

    logging.info("Folder structure and SDE connections created successfully.")