import argparse
import logging
import multiprocessing
import sys

import gentle


def main(txtfile=None, audiofile=None):
    parser = argparse.ArgumentParser(
            description='Align a transcript to audio by generating a new language model.  Outputs JSON')
    parser.add_argument(
            '--nthreads', default=multiprocessing.cpu_count(), type=int,
            help='number of alignment threads')
    parser.add_argument(
            '-o', '--output', metavar='output', type=str,
            help='output filename')
    parser.add_argument(
            '--conservative', dest='conservative', action='store_true',
            help='conservative alignment')
    parser.set_defaults(conservative=False)
    parser.add_argument(
            '--disfluency', dest='disfluency', action='store_true',
            help='include disfluencies (uh, um) in alignment')
    parser.set_defaults(disfluency=False)
    parser.add_argument(
            '--log', default="INFO",
            help='the log level (DEBUG, INFO, WARNING, ERROR, or CRITICAL)')
    parser.add_argument(
            'audiofile', type=str,
            help='audio file')
    parser.add_argument(
            'txtfile', type=str,
            help='transcript text file')
    args = parser.parse_args()

    log_level = args.log.upper()
    logging.getLogger().setLevel(log_level)

    disfluencies = {'uh', 'um'}

    def on_progress(p):
        for k, v in p.items():
            logging.debug("%s: %s" % (k, v))

    txtfile = args.txtfile if txtfile is None else txtfile
    audiofile = args.audiofile if audiofile is None else audiofile

    with open(txtfile) as fh:
        transcript = fh.read()

    resources = gentle.Resources()
    logging.info("converting audio to 8K sampled wav")

    with gentle.resampled(audiofile) as wavfile:
        logging.info("starting alignment")
        aligner = gentle.ForcedAligner(resources, transcript, nthreads=args.nthreads, disfluency=args.disfluency,
                                       conservative=args.conservative, disfluencies=disfluencies)
        result = aligner.transcribe(wavfile, progress_cb=on_progress, logging=logging)

    fh = open(args.output, 'w') if args.output else sys.stdout
    fh.write(result.to_json(indent=2))
    if args.output:
        logging.info("output written to %s" % args.output)
    return result.to_json()

if __name__ == '__main__':
    main()
