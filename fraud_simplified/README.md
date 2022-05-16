## Development Status

### Notebooks

- `2_training_dataset_creation.ipynb`
    - There is a prefix bug when making join queries (minor issue).
    - Chronological split is not implemented (needed for this tutorial).
    - Datasets can't be downloaded locally easily (`td.read()`).

### Dependencies

At the time of development, we needed to install libraries from GitHub:
- hsfs (fix for the transformation error)

That is, some notebooks will not work with the libraries on PyPi (unless they have been updated).