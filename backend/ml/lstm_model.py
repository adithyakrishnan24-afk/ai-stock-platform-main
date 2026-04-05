# LSTM module intentionally disabled
# Reason: TensorFlow dependency optional for this project

def lstm_predict(*args, **kwargs):
    raise NotImplementedError("LSTM model disabled (TensorFlow not installed)")