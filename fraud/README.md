## Development Status

### Notebooks

- `2_training_dataset_creation.ipynb`
    - Min-max scaling does not work when using a splitted dataset.
    - There is a prefix bug when making join queries (minor issue).
    - Chronological split is not implemented (needed for this tutorial).
    - Datasets can't be downloaded locally easily (`td.read()`).
- `3_experimentation.ipynb`
    - This notebooks must be run in a PySpark kernel because of Maggy.
    - We would like to use `gridsearch` instead of `randomsearch`, but it does not work at the moment.
- `4_model_training_and_registration.ipynb`
    - The old Hopsworks UI has to be used (to enable serving).
- `5_model_serving.ipynb`
    - There is an error message when deploying models (even though it works).
    - The old Hopsworks UI has to be used (to setup REST API).
    - A small part of the code (based on [this example](https://hopsworks.readthedocs.io/en/latest/hopsml/python_model_serving.html#serving-python-based-models-on-hopsworks)) uses the old `hops` library.
- `6_job_scheduling.ipynb`
    - The old Hopsworks UI has to be used.

### Dependencies

At the time of development, we needed to install two libraries from GitHub:
- hsml: https://github.com/robzor92/machine-learning-api@branch-2.5#egg=hsml&subdirectory=python
- hopsworks: https://github.com/logicalclocks/hopsworks-api@main#egg=hopsworks&subdirectory=python

That is, some notebooks will not work with the libraries on PyPi (unless they have been updated).