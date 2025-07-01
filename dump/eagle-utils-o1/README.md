# eagle-utils

This repository provides utility functions for other repositories. The `release` branch contains a clean set of JavaScript files that can be used as a submodule or pulled directly.

## Usage

### As a Submodule
Add this repository as a submodule in your project:
```bash
git submodule add -b release https://github.com/eagle-help/eagle-utils.git path/to/your/utils
```

### Pulling Directly
```bash
git clone -b release https://github.com/eagle-help/eagle-utils.git path/to/utils
```


## Structure
The `release` branch contains only the necessary JavaScript files at the root level, ensuring a clean and minimal setup.

## Contributing
- Development happens on the `main` branch.
- The `release` branch is automatically updated with the latest utils from `main`.

## License
This project is licensed under the [MIT License](LICENSE).