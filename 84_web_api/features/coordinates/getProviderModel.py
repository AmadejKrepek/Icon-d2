import os


def getProviderModel(parameter):
    # Determine the provider_id and model_id based on the table name
    if parameter.endswith("_icond2"):
        provider_id = os.getenv("DWD_PROVIDER_ID")  # Set the appropriate ID for icond2
        model_id = os.getenv("DWD_MODEL_ID")  # Set the appropriate ID for icond2
        return provider_id, model_id
    elif parameter.endswith("_aladin"):
        provider_id = os.getenv("ARSO_PROVIDER_ID")  # Set the appropriate ID for aladin
        model_id = os.getenv("ARSO_MODEL_ID")  # Set the appropriate ID for aladin
        return provider_id, model_id
    else:
        print("Invalid table name format. The table name should end with '_icond2' or '_aladin'.")
        exit(1)
