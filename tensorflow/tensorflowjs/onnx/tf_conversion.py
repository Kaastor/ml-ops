import os

# python -m tf2onnx.convert --saved-model ./saved-model --output model.onnx --opset=10
os.system('python3 -m tf2onnx.convert --saved-model ../url/conv-ae/last-saved-model --output ./model.onnx --opset=10')
