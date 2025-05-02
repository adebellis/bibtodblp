# bibtodblp

📚 A command-line tool to automatically update your `.bib` file entries with verified citations from [DBLP](https://dblp.org).

## ✨ Features

- Searches DBLP via public search API.
- Interactive selection of references. 
- Replaces old BibTeX entries with accurate ones from DBLP.
- Condensed or full BibTeX format.
- Fallback to original if no match found.

## 📦 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/bibtodblp.git
cd bibtodblp
pip install -r requirements.txt
```


## 🚀 Usage

``` bash
python main.py --input path/to/your.bib --condensed
```

| Argument      | Description                                                                  |
| ------------- | ---------------------------------------------------------------------------- |
| `--input`     | **Required**: Path to the input `.bib` file                                  |
| `--output`    | **Optional**: Path to the output `.bib` file (default: `inputname_dblp.bib`) |
| `--condensed` | **Optional**: Use condensed citation style from DBLP (false by default)      |


## 🧪 Example

Original:

```bibtex
@inproceedings{vaswani2017attention,
  title={Attention is All You Need},
  author={Vaswani and others},
}
```

Updated (condensed):

```bibtex
% DBLP ID: conf/nips/VaswaniSPUJGKP17
@inproceedings{vaswani2017attention,
  author       = {Ashish Vaswani and
                  Noam Shazeer and
                  Niki Parmar and
                  Jakob Uszkoreit and
                  Llion Jones and
                  Aidan N. Gomez and
                  Lukasz Kaiser and
                  Illia Polosukhin},
  title        = {Attention is All you Need},
  booktitle    = {{NIPS}},
  pages        = {5998--6008},
  year         = {2017}
}
```


## 📜 License

This project is licensed under the MIT License.

## 🤝 Contributing

Feel free to open issues or pull requests! Suggestions and improvements welcome.
