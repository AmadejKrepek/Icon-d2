def remove_leading_zeros(last_model_run):
    if last_model_run.startswith('00'):
        # Replace only the first '0' with an empty string
        last_model_run = last_model_run.replace('0', '', 1)
    else:
        # Remove all leading zeros
        last_model_run = last_model_run.lstrip('0')
    
    return last_model_run