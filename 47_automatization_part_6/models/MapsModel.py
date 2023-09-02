class MapsModel:
    def __init__(self, df, variable, title, x_title, colormap, legend_ticks, contour_levels, output_filepath, model_run_formatted_date, selected_formatted_date, custom_font):
        self.df = df
        self.variable = variable
        self.title = title
        self.x_title = x_title
        self.colormap = colormap
        self.legend_ticks = legend_ticks
        self.contour_levels = contour_levels
        self.output_filepath = output_filepath
        self.model_run_formatted_date = model_run_formatted_date
        self.selected_formatted_date = selected_formatted_date
        self.custom_font = custom_font