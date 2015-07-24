"""
PHYLIP multiple sequence alignment format (:mod:`skbio.io.format.phylip`)
=========================================================================

.. currentmodule:: skbio.io.format.phylip

The PHYLIP file format stores a multiple sequence alignment. The format was
originally defined and used in Joe Felsenstein's PHYLIP package [1]_, and has
since been supported by several other bioinformatics tools (e.g., RAxML [2]_).
See [3]_ for the original format description, and [4]_ and [5]_ for additional
descriptions.

An example PHYLIP-formatted file taken from [3]_::

          5    42
    Turkey    AAGCTNGGGC ATTTCAGGGT GAGCCCGGGC AATACAGGGT AT
    Salmo gairAAGCCTTGGC AGTGCAGGGT GAGCCGTGGC CGGGCACGGT AT
    H. SapiensACCGGTTGGC CGTTCAGGGT ACAGGTTGGC CGTTCAGGGT AA
    Chimp     AAACCCTTGC CGTTACGCTT AAACCGAGGC CGGGACACTC AT
    Gorilla   AAACCCTTGC CGGTACGCTT AAACCATTGC CGGTACGCTT AA

.. note:: Original copyright notice for the above PHYLIP file:

   *(c) Copyright 1986-2008 by The University of Washington. Written by Joseph
   Felsenstein. Permission is granted to copy this document provided that no
   fee is charged for it and that this copyright notice is not removed.*

Format Support
--------------
**Has Sniffer: Yes**

+------+------+---------------------------------------------------------------+
|Reader|Writer|                          Object Class                         |
+======+======+===============================================================+
|Yes   |Yes   |:mod:`skbio.alignment.Alignment`                               |
+------+------+---------------------------------------------------------------+

Format Specification
--------------------
PHYLIP format is a plain text format containing exactly two sections: a header
describing the dimensions of the alignment, followed by the multiple sequence
alignment itself.

The format described here is "strict" PHYLIP, as described in [4]_. Strict
PHYLIP requires that each sequence identifier is exactly 10 characters long
(padded with spaces as necessary). Other bioinformatics tools (e.g., RAxML) may
relax this rule to allow for longer sequence identifiers. See the
**Alignment Section** below for more details.

The format described here is "sequential" format. The original PHYLIP format
specification [3]_ describes both sequential and interleaved formats.

.. note:: scikit-bio currently only supports writing strict, sequential
   PHYLIP-formatted files from an ``skbio.alignment.Alignment``. It does not
   yet support reading PHYLIP-formatted files, nor does it support relaxed or
   interleaved PHYLIP formats.

Header Section
^^^^^^^^^^^^^^
The header consists of a single line describing the dimensions of the
alignment. It **must** be the first line in the file. The header consists of
optional spaces, followed by two positive integers (``n`` and ``m``) separated
by one or more spaces. The first integer (``n``) specifies the number of
sequences (i.e., the number of rows) in the alignment. The second integer
(``m``) specifies the length of the sequences (i.e., the number of columns) in
the alignment. The smallest supported alignment dimensions are 1x1.

.. note:: scikit-bio will write the PHYLIP format header *without* preceding
   spaces, and with only a single space between ``n`` and ``m``.

   PHYLIP format *does not* support blank line(s) between the header and the
   alignment.

Alignment Section
^^^^^^^^^^^^^^^^^
The alignment section immediately follows the header. It consists of ``n``
lines (rows), one for each sequence in the alignment. Each row consists of a
sequence identifier (ID) and characters in the sequence, in fixed width format.

The sequence ID can be up to 10 characters long. IDs less than 10 characters
must have spaces appended to them to reach the 10 character fixed width. Within
an ID, all characters except newlines are supported, including spaces,
underscores, and numbers.

.. note:: While not explicitly stated in the original PHYLIP format
   description, scikit-bio only supports writing unique sequence identifiers
   (i.e., duplicates are not allowed). Uniqueness is required because an
   ``skbio.alignment.Alignment`` cannot be created with duplicate IDs.

   scikit-bio supports the empty string (``''``) as a valid sequence ID. An
   empty ID will be padded with 10 spaces.

Sequence characters immediately follow the sequence ID. They *must* start at
the 11th character in the line, as the first 10 characters are reserved for the
sequence ID. While PHYLIP format does not explicitly restrict the set of
supported characters that may be used to represent a sequence, the original
format description [3]_ specifies the IUPAC nucleic acid lexicon for DNA or RNA
sequences, and the IUPAC protein lexicon for protein sequences. The original
PHYLIP specification uses ``-`` as a gap character, though older versions also
supported ``.``. The sequence characters may contain optional spaces (e.g., to
improve readability), and both upper and lower case characters are supported.

.. note:: scikit-bio will write a PHYLIP-formatted file even if the alignment's
   sequence characters are not valid IUPAC characters. This differs from the
   PHYLIP specification, which states that a PHYLIP-formatted file can only
   contain valid IUPAC characters. To check whether all characters are valid
   before writing, the user can call ``Alignment.is_valid()``.

   Since scikit-bio supports both ``-`` and ``.`` as gap characters (e.g., in
   ``skbio.alignment.Alignment``), both are supported when writing a
   PHYLIP-formatted file.

   When writing a PHYLIP-formatted file, scikit-bio will split up each sequence
   into chunks that are 10 characters long. Each chunk will be separated by a
   single space. The sequence will always appear on a single line (sequential
   format). It will *not* be wrapped across multiple lines. Sequences are
   chunked in this manner for improved readability, and because most example
   PHYLIP files are chunked in a similar way (e.g., see the example file
   above). Note that this chunking is not required by the PHYLIP format.

Examples
--------
Let's create an alignment with three DNA sequences of equal length:

>>> from skbio import Alignment, DNA
>>> seqs = [DNA('ACCGTTGTA-GTAGCT', metadata={'id':'seq1'}),
...         DNA('A--GTCGAA-GTACCT', metadata={'id':'sequence-2'}),
...         DNA('AGAGTTGAAGGTATCT', metadata={'id':'3'})]
>>> aln = Alignment(seqs)
>>> aln
<Alignment: n=3; mean +/- std length=16.00 +/- 0.00>

Now let's write the alignment to file in PHYLIP format, and take a look at the
output:

>>> from io import StringIO
>>> fh = StringIO()
>>> print(aln.write(fh, format='phylip').getvalue())
3 16
seq1      ACCGTTGTA- GTAGCT
sequence-2A--GTCGAA- GTACCT
3         AGAGTTGAAG GTATCT
<BLANKLINE>
>>> fh.close()

Notice that the 16-character sequences were split into two chunks, and that
each sequence appears on a single line (sequential format). Also note that each
sequence ID is padded with spaces to 10 characters in order to produce a fixed
width column.

If the sequence IDs in an alignment surpass the 10-character limit, an error
will be raised when we try to write a PHYLIP file:

>>> long_id_seqs = [DNA('ACCGT', metadata={'id':'seq1'}),
...                 DNA('A--GT', metadata={'id':'long-sequence-2'}),
...                 DNA('AGAGT', metadata={'id':'seq3'})]
>>> long_id_aln = Alignment(long_id_seqs)
>>> fh = StringIO()
>>> long_id_aln.write(fh, format='phylip')
Traceback (most recent call last):
    ...
PhylipFormatError: Alignment can only be written in PHYLIP format if all \
sequence IDs have 10 or fewer characters. Found sequence with ID \
'long-sequence-2' that exceeds this limit. Use Alignment.update_ids to assign \
shorter IDs.
>>> fh.close()

One way to work around this is to update the IDs to be shorter. The recommended
way of accomplishing this is via ``Alignment.update_ids``, which provides a
flexible way of creating a new ``Alignment`` with updated IDs. For example, to
remap each of the IDs to integer-based IDs:

>>> short_id_aln, _ = long_id_aln.update_ids()
>>> short_id_aln.ids()
['1', '2', '3']

We can now write the new alignment in PHYLIP format:

>>> fh = StringIO()
>>> print(short_id_aln.write(fh, format='phylip').getvalue())
3 5
1         ACCGT
2         A--GT
3         AGAGT
<BLANKLINE>
>>> fh.close()

References
----------
.. [1] http://evolution.genetics.washington.edu/phylip.html
.. [2] RAxML Version 8: A tool for Phylogenetic Analysis and
   Post-Analysis of Large Phylogenies". In Bioinformatics, 2014
.. [3] http://evolution.genetics.washington.edu/phylip/doc/sequence.html
.. [4] http://www.phylo.org/tools/obsolete/phylip.html
.. [5] http://www.bioperl.org/wiki/PHYLIP_multiple_alignment_format

"""

# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import string
from functools import partial

from skbio.alignment import Alignment, SequenceCollection
from skbio.sequence import Sequence, DNA, RNA, Protein
from skbio.io import create_format, PhylipFormatError
from skbio.util._misc import chunk_str
from skbio.io.format._base import _line_generator, _get_nth_sequence


phylip = create_format('phylip')


@phylip.sniffer()
def _phylip_sniffer(fh):
    # Strategy:
    #   Read the header and a single sequence; verify that the sequence length
    #   matches the header information.  Do not verify that the total number of
    #   lines matches the header information, since that would require reading
    #   the whole file.
    try:
        header = next(_line_generator(fh))
        _, seq_len = _parse_phylip_header(header, True)
        line = next(_line_generator(fh))
        #_validate_line(line, seq_len)
    except (StopIteration, PhylipFormatError):
        return False, {}
    return True, {}


_whitespace_translate_table = str.maketrans(
    {c: '' for c in string.whitespace}
)


def _parse_phylip_header(header, raise_exc=False):
    """Parses the header of a PHYLIP file"""

    parts = header.split()

    if len(parts) != 2:
        if raise_exc:
            raise PhylipFormatError(
                "Could not parse the header of a PHYLIP file. It should "
                "contain only two integers, but we found %d elements on this "
                "line.\nThe line we tried to parse: \n\n '%s'" % (
                    len(parts), header.strip()
                )
            )
        else:
            return None

    try:
        return (int(parts[0]), int(parts[1]))
    except ValueError:
        if raise_exc:
            raise PhylipFormatError(
                "Could not the parse the header of a PHYLIP file. The values "
                "on this line are not integers.\nThe line we tried to parse:"
                "\n\n'%s'" % header.strip()
            )
        else:
            return None


def relaxed_ids(line, delimiters=string.whitespace):
    pos = min(line.find(c) for c in delimiters if line.find(c) > 0)
    id_ = line[0:pos]
    sequence = line[pos:].translate(_whitespace_translate_table)

    return (sequence, id_)


def strict_ids(line, id_length=10):
    id_ = line[0:id_length]
    sequence = line[id_length:].translate(_whitespace_translate_table)

    return (sequence, id_)


def _parse_phylip_raw(fh, data_parser, interleaved=False):
    """Raw parser for PHYLIP files."""

    phylip_iter = _line_generator(fh, skip_blanks=True)
    header = next(phylip_iter)
    num_seq, seq_len = _parse_phylip_header(header, raise_exc=True)

    for line in phylip_iter:
        sequence, id_ = data_parser(line)

        if len(sequence) == seq_len:
            yield (sequence, id_)
        else:
            pass  # TODO: Parse sequences in interleaved format


@phylip.reader
def _phylip_to_generator(fh, data_parser=strict_ids, interleaved=False,
                         constructor=Sequence):
    for seq, id_ in _parse_phylip_raw(fh, data_parser, interleaved):
        yield constructor(seq, metadata={'id': id_})


@phylip.reader(Sequence)
def _phylip_to_sequence(fh, data_parser=strict_ids, interleaved=False,
                        seq_num=1):
    return _get_nth_sequence(
        _phylip_to_generator(fh, data_parser=data_parser,
                             interleaved=interleaved, constructor=Sequence),
        seq_num
    )


@phylip.reader(DNA)
def _phylip_to_dna_sequence(fh, data_parser=strict_ids, interleaved=False,
                            seq_num=1):
    return _get_nth_sequence(
        _phylip_to_generator(
            fh, data_parser=data_parser,
            interleaved=interleaved,
            constructor=partial(DNA, validate=False)
        ),
        seq_num
    )


@phylip.reader(RNA)
def _phylip_to_rna_sequence(fh, data_parser=strict_ids, interleaved=False,
                            seq_num=1):
    return _get_nth_sequence(
        _phylip_to_generator(
            fh, data_parser=data_parser,
            interleaved=interleaved,
            constructor=partial(RNA, validate=False)
        ),
        seq_num
    )


@phylip.reader(Protein)
def _phylip_to_protein_sequence(fh, data_parser=strict_ids,
                                interleaved=False, seq_num=1):
    return _get_nth_sequence(
        _phylip_to_generator(
            fh, data_parser=data_parser,
            interleaved=interleaved,
            constructor=partial(Protein, validate=False)
        ),
        seq_num
    )


@phylip.reader(SequenceCollection)
def _phylip_to_sequence_collection(fh, data_parser=strict_ids,
                                   interleaved=False, constructor=Sequence):
    return SequenceCollection(
        list(_phylip_to_generator(
            fh, data_parser=data_parser,
            interleaved=interleaved, constructor=constructor
        ))
    )


@phylip.reader(Alignment)
def _phylip_to_alignment(fh, data_parser=strict_ids, interleaved=False,
                         constructor=Sequence):
    return Alignment(
        list(_phylip_to_generator(
            fh, data_parser=data_parser,
            interleaved=interleaved, constructor=constructor
        ))
    )


@phylip.writer(Alignment)
def _alignment_to_phylip(obj, fh):

    if obj.is_empty():
        raise PhylipFormatError(
            "Alignment can only be written in PHYLIP format if there is at "
            "least one sequence in the alignment.")

    sequence_length = obj.sequence_length()
    if sequence_length == 0:
        raise PhylipFormatError(
            "Alignment can only be written in PHYLIP format if there is at "
            "least one position in the alignment.")

    chunk_size = 10
    for id_ in obj.ids():
        if len(id_) > chunk_size:
            raise PhylipFormatError(
                "Alignment can only be written in PHYLIP format if all "
                "sequence IDs have %d or fewer characters. Found sequence "
                "with ID '%s' that exceeds this limit. Use "
                "Alignment.update_ids to assign shorter IDs." %
                (chunk_size, id_))

    sequence_count = obj.sequence_count()
    fh.write('{0:d} {1:d}\n'.format(sequence_count, sequence_length))

    fmt = '{0:%d}{1}\n' % chunk_size
    for seq in obj:
        chunked_seq = chunk_str(str(seq), chunk_size, ' ')
        fh.write(fmt.format(seq.metadata['id'], chunked_seq))
