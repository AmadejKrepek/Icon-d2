class MapsModel:
    def __init__(self, df, variable, title, x_title, colormap, legend_ticks, contour_levels, model_run_formatted_date,
                 selected_formatted_date, model_run_model, provider, custom_font):
        self.df = df
        self.variable = variable
        self.title = title
        self.x_title = x_title
        self.colormap = colormap
        self.legend_ticks = legend_ticks
        self.contour_levels = contour_levels
        self.model_run_formatted_date = model_run_formatted_date
        self.selected_formatted_date = selected_formatted_date
        self.model_run_model = model_run_model
        self.provider = provider
        self.custom_font = custom_font
