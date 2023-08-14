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
        subparser.add_argument('-f', '--force', action='store_true', default = False, help='write signature even if no hashes remain after subtraction')
        subparser.add_argument('-o', '--out', type=str, help='path to output signature file', required=True)

    def main(self, args):
        # code that we actually run.
        super().main(args)

        all_sketches = list(args.sketches)
        main_sketch = all_sketches[0]
        other_sketches = all_sketches[1:]

        main_sig = sourmash.load_one_signature(main_sketch, ksize=args.k)
        main_kmers = dict(main_sig.minhash.hashes)


        # Check if there's abundance in the minhash
        if not main_sig.minhash.track_abundance:
            error("There is no abundance in the minhash.\nPlease use 'sourmash sig subtract' instead.")
            sys.exit(1)
            
        removed_kmers = 0
        for sketch_filename in other_sketches:
            notify(f"Subtracting {sketch_filename}")
            if not main_kmers:
                error("No kmers left to subtract")
                if args.force:
                    notify("Forcing output")
                    final_mh = main_sig.minhash.copy_and_clear().flatten()
                    finalSig = sourmash.SourmashSignature(final_mh)
                    with sourmash.sourmash_args.FileOutput(args.out, 'wt') as fp:
                        sourmash.save_signatures([finalSig], fp=fp)
                    notify(f"Saved final EMPTY signature to '{args.out}'")
                    sys.exit(0)
                    
                sys.exit(1)
            try:
                sig = sourmash.load_one_signature(sketch_filename, ksize=args.k)
            except Exception as e:
                error(f"Error while loading signature from '{sketch_filename}'\nAre you sure it's a valid signature file and kSzie?\n{e}")
                sys.exit(1)

            for hashed_kmer in sig.minhash.hashes.keys():
                if hashed_kmer in main_kmers:
                    removed_kmers += 1
                    main_kmers.pop(hashed_kmer)            

        final_mh = main_sig.minhash.copy_and_clear().flatten()
        final_mh.add_many(main_kmers.keys())
        final_mh = final_mh.inflate(main_sig.minhash)

        finalSig = sourmash.SourmashSignature(final_mh)
        with sourmash.sourmash_args.FileOutput(args.out, 'wt') as fp:
            sourmash.save_signatures([finalSig], fp=fp)

        notify(f"Removed {removed_kmers} kmers.")
        notify(f"Saved final signature to '{args.out}'")