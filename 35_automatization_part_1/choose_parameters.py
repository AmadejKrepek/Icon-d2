from find_latest_model_run_top import get_latest_model_run_filename, download_and_extract_log_file
from datetime import datetime

variable_names = [
    "dbz_cmax", "tcm", "snowc", "qv_s", "avmfl_s", "tch", "tcond10_mx",
    "w_i", "tqg", "snowlmt", "ceiling", "asob_t", "tqr", "t_snow", "echotop",
    "dbz_850", "tqc_dia", "tmax_2m", "c_t_lk", "tmin_2m", "uh_max", "tqv_dia",
    "h_ice", "t_2m", "w_snow", "td_2m", "tqs", "aswdir_s", "u_10m", "alb_rad",
    "alhfl_s", "runoff_g", "athb_t", "clch", "clcm", "clcl", "t_mnw_lk",
    "tqc", "prg_gsp", "freshsnw", "htop_dc", "htop_sc", "runoff_s", "tqi_dia",
    "sdi_2", "rain_gsp", "twater", "vmax_10m", "ww", "h_snow", "ps", "tqi",
    "prr_gsp", "athb_s", "aswdifd_s", "t_ice", "aswdifu_s", "rain_con",
    "prs_gsp", "tot_prec", "vorw_ctmax", "hbas_sc", "relhum_2m", "tcond_max",
    "mh", "snow_con", "hzerocl", "pmsl", "cldepth", "t_g", "lpi_max",
    "apab_s", "tqv", "aumfl_s", "h_ml_lk", "clct_mod", "snow_gsp", "asob_s",
    "grau_gsp", "cin_ml", "v_10m", "t_bot_lk", "t_wml_lk", "cape_ml", "z0",
    "clct", "ashfl_s", "rho_snow", "lpi", "w_ctmax"
]

def main():
    print("Script started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    data = download_and_extract_log_file()

    print("Available parameters:")
    for idx, param in enumerate(variable_names, start=1):
        print(f"{idx}. {param}")

    parameter_input = input("Enter parameter numbers separated by commas: ")
    selected_indices = [int(idx.strip()) for idx in parameter_input.split(",")]

    selected_params = []
    for idx in selected_indices:
        if 1 <= idx <= len(variable_names):
            selected_params.append(variable_names[idx - 1])
        else:
            print(f"Invalid index {idx}. Skipping.")

    if not selected_params:
        print("No valid parameters selected. Exiting.")
        return

    print("Searching for model runs...")
    filenames = []
    for param in selected_params:
        latest_file = get_latest_model_run_filename(data, param)
        if latest_file:
            filenames.append(latest_file)
            print(f"Latest model run filename for parameter '{param}': {latest_file}")
        else:
            print(f"No regular-lat-lon model run found for parameter '{param}'.")

    if not filenames:
        print("No filenames available for the selected parameters.")

    print("Script finished at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()