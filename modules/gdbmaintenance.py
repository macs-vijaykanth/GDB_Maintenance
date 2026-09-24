import os
import logging
import arcpy
from datetime import date
from modules.send_failure_email import send_failure_email

def gdbmaintenance(settings):
    # Define the base folder containing subfolders
    # Get the current directory of main.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory of the current directory
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

    # Define the new base folder path
    base_folder = os.path.join(parent_dir, "Databases")

    # Loop through subfolders
    for subfolder in os.listdir(base_folder):
        subfolder_path = os.path.join(base_folder, subfolder)
        if not os.path.isdir(subfolder_path):
            continue
        connection_file = os.path.join(subfolder_path, "Admin", "admin_connection.sde")

        if os.path.exists(connection_file):
            sdeConnectionString = connection_file
            folder_path = f"{base_folder}\\{subfolder}\\DataOwners"

            logging.debug("Geodatabase Maintenance script starting for {0}".format(settings.client_name))

            try:
                arcpy.env.workspace = sdeConnectionString
                arcpy.env.overwriteOutput = True

                logging.debug("Environment set to {0}".format(subfolder) + " admin connection")
                arcpy.ClearWorkspaceCache_management()

                logging.debug("The database is no longer accepting connections")
                arcpy.AcceptConnections(sdeConnectionString, False)

                logging.debug("Disconnecting all users")
                arcpy.DisconnectUser(sdeConnectionString, "ALL")

                logging.debug("Running compress")
                arcpy.Compress_management(sdeConnectionString)

                logging.debug("Allow users to connect to the database again")
                arcpy.AcceptConnections(sdeConnectionString, True)

                logging.debug("Rebuilding indexes on the system tables")
                arcpy.RebuildIndexes_management(sdeConnectionString, "SYSTEM", "", "ALL")

                logging.debug("Updating statistics on the system tables")
                arcpy.AnalyzeDatasets_management(sdeConnectionString, "SYSTEM", "", "ANALYZE_BASE", "ANALYZE_DELTA", "ANALYZE_ARCHIVE")

            except Exception as e:
                logging.info(str(e))
                logging.info(arcpy.GetMessages(2))
                logging.error(arcpy.GetMessages(2))
                logging.error(str(e))
                send_failure_email(settings, str(e), f"Admin maintenance for {subfolder}")

            finally:
                logging.info("Maintenance completed for admin connection to {0}".format(subfolder) + " geodatabase.")

            connection_strings = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.sde')]

            for daConnectionString in connection_strings:
                logging.debug("Maintenance script starting for dataowner: {0}".format(daConnectionString))

                try:
                    arcpy.env.workspace = daConnectionString
                    workspace = arcpy.env.workspace

                    logging.debug("Environment set to {0}".format(daConnectionString))
                    userName = arcpy.Describe(arcpy.env.workspace).connectionProperties.user
                    logging.debug("Connected with {0}".format(userName) + " user")

                    oDataList = arcpy.ListTables(userName + '*') + arcpy.ListFeatureClasses(userName + '*') + arcpy.ListRasters(userName + '*')
                    

                    for dataset in arcpy.ListDatasets(userName + '*'):
                        oDataList += arcpy.ListFeatureClasses(feature_dataset=dataset)
            
                    logging.debug("Tables to be included {0}".format(oDataList))
                    
                    logging.info("Test before RebuildIndexe")

                    arcpy.RebuildIndexes_management(workspace, "NO_SYSTEM", oDataList, "ALL")
                    logging.debug("Rebuild indexes complete")

                    arcpy.AnalyzeDatasets_management(workspace, "NO_SYSTEM", oDataList, "ANALYZE_BASE", "ANALYZE_DELTA", "ANALYZE_ARCHIVE")
                    logging.debug("Analyze datasets complete")

                except Exception as e:
                    logging.info(str(e))
                    logging.info(arcpy.GetMessages(2))
                    logging.error(arcpy.GetMessages(2))
                    logging.error(str(e))
                    send_failure_email(settings, str(e), f"DataOwner maintenance for {userName} in {subfolder}")

                finally:
                    logging.info("Maintenance completed for {0}".format(userName) + " user in {0}".format(subfolder) + " geodatabase.")
        else:
            logging.warning(f"Connection file not found: {connection_file}")

        logging.info("Geodatabase Maintenance Activity is complete")

