from db_reader import read_data_and_generate_csv, select_table

selected_table = select_table()
if selected_table:
    output_file = input("Enter the output file name: ")  # Get the output file name from the user
    read_data_and_generate_csv(selected_table, output_file)