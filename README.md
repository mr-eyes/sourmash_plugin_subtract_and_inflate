# sourmash_plugin_subtract_and_inflate

sourmash does not currently support keeping abundance when subtracting two signatures. A possible solution is to do `sourmash sig subtract` and then `sourmash sig inflate`. This plugin does this in one step. It subtracts signatures from the first signature and then inflates its abundance (recovers the abundance). **The plugin also works on differently scaled signatures.**

## Installation

Make sure you have an updated pip version:

```bash
# update pip
pip install --upgrade pip

# or 
conda update pip
```

Then install the plugin:


```
pip install git+https://github.com/mr-eyes/sourmash_plugin_subtract_and_inflate
```

## Usage example

This will subtract all of the hashes in `sketch_1.sig` and `sketch_2.sig` from `main_sketch.sig` and save it to `subtracted.sig`.

```bash
sourmash scripts subtract_and_inflate -k 51 -o subtracted.sig main_sketch.sig sketch_1.sig sketch_2.sig ...
```

```bash
usage:  subtract_and_inflate [-h] [-q] [-d] -k K -o OUT sketches [sketches ...]

positional arguments:
  sketches           file(s) containing two or more sketches

options:
  -h, --help         show this help message and exit
  -q, --quiet        suppress non-error output
  -d, --debug        provide debugging output
  -k K               kmer size
  -o OUT, --out OUT  path to output signature file
```