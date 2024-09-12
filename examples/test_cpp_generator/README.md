# test_cpp_generator.py

### Updating unit tests fixed data
After changing a unit test the fixed data needs to be updated to successfully pass the unit tests.

```bash
python -c 'cpp_generator_tests import generate_reference_code; generate_reference_code()'
```

After executing that command, the fixed data under `tests/` will be updated and will need to be committed to git.
