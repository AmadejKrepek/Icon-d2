from db_reader import read_data_and_generate_csv, select_table

selected_table = select_table()
if selected_table:
    output_file = input("Enter the name of the output CSV file: ")
    read_data_and_generate_csv(selected_table, output_file)
