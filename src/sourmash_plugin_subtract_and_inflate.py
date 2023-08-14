"""\
    sourmash does not support keeping abundance when subtracting two signatures.
    This plugin subtract signatures from the first signature and then inflate 
    its abundance (recover the abundance of the first signature). 
"""

usage="""
   sourmash scripts subtract_and_inflate -k <ksize> -o <output> <signature1> <signature2> [<signature3> ...]
"""

epilog="""
See https://github.com/mr-eyes/sourmash_plugin_subtract_and_inflate for more examples.

Need help? Have questions? Ask at https://github.com/mr-eyes/sourmash_plugin_subtract_and_inflate/issues OR http://github.com/sourmash/issues!
"""


import argparse
import sourmash
from sourmash.plugins import CommandLinePlugin
from sourmash.logging import error, notify
import sys


"""
TODO:
    - Support subtracting rare kmers only
    - Support Subtracting overabundant kmers only
"""


class Command_SubtractAndInflate(CommandLinePlugin):
    command = 'subtract_and_inflate'             # 'scripts <command>'
    description = __doc__       # output with -h
    usage = usage               # output with no args/bad args as well as -h
    epilog = epilog             # output with -h
    formatter_class = argparse.RawTextHelpFormatter # do not reformat multiline

    def __init__(self, subparser):
        super().__init__(subparser)

        subparser.add_argument('sketches', nargs='+', help="file(s) containing two or more sketches")
        subparser.add_argument('-k', type=int, help='kmer size', required=True)
        subparser.add_argument('-o', '--out', type=str, help='path to output signature file', required=True)

    def main(self, args):
        # code that we actually run.
        super().main(args)

        all_sketches = list(args.sketches)
        main_sketch = all_sketches[0]
        other_sketches = all_sketches[1:]

        main_sig = sourmash.load_file_as_signatures(main_sketch, ksize=args.ksize)
        main_kmers = set(main_sig.minhash.keys())
        # Check if there's abundance in the minhash
        if not main_sig.minhash.track_abundance:
            error("There is no abundance in the minhash.\nPlease use 'sourmash sig subtract' instead.")
            sys.exit(1)

        for sketch_filename in other_sketches:
            notify(f"Subtracting {sketch_filename}")
            if len(main_kmers) == 0:
                error("No kmers left to subtract")
                sys.exit(1)
            try:
                sig = sourmash.load_file_as_signatures(sketch_filename, ksize=args.ksize)
            except Exception as e:
                error(f"Error while loading signature from '{sketch_filename}'\nAre you sure it's a valid signature file and kSzie?\n{e}")
                sys.exit(1)

            main_kmers -= set(sig.minhash.keys())

        final_mh = main_sig.minhash.copy_and_clear().flatten()
        final_mh.add_many(main_kmers)
        final_mh = final_mh.inflate(main_sig.minhash)

        finalSig = sourmash.SourmashSignature(final_mh)
        with sourmash.sourmash_args.FileOutput(args.out, 'wt') as fp:
            sourmash.save_signatures([finalSig], fp=fp)
            
        notify(f"Saved final signature to '{args.out}'")