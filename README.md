# LSTM-CRF in PyTorch

A PyTorch implementation of bidirectional LSTM-CRF for sequence tagging, adapted from [the PyTorch tutorial](http://pytorch.org/tutorials/beginner/nlp/advanced_tutorial.html).

## Usage

To train:
```
python train.py model tag_to_idx word_to_idx training_data num_epoch
```

To predict:
```
python predict.py model tag_to_idx word_to_idx test_data
```
