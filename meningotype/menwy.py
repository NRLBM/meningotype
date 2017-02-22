#!/usr/bin/env python
# Script by Jason Kwong
# Checks for dual W+Y antigenic specificity of Neisseria meningitidis

# Use modern print function from python 3.x
from __future__ import print_function

# Modules
import argparse
from argparse import RawTextHelpFormatter
import os
from Bio import SeqIO
from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast import NCBIXML
from pkg_resources import resource_string, resource_filename

# Local modules
import nmen

# BLAST
def seqBLAST(f):
	fBLAST = NcbiblastnCommandline(query=f, db=blastdb, outfmt="'6 qseqid sstrand qstart qend sstart send slen'", dust='no', culling_limit=1)
	stdout, stderr = fBLAST()
	blastOUT = stdout.split('\t')
	if len(blastOUT) == 7:
		blast_qseqid = blastOUT[0]
		blast_sstrand = blastOUT[1]
		blast_qstart = int(blastOUT[2])
		blast_qend = int(blastOUT[3])
		blast_sstart = int(blastOUT[4])
		blast_send = int(blastOUT[5])
		blast_slen = int(blastOUT[6])
		for s in SeqIO.parse(f, 'fasta'):
			if s.id == blastOUT[0]:
				blastCONTIG = s.seq
		if blast_sstrand == 'plus':
			synG_SEQ = blastCONTIG[blast_qstart-1:blast_qend]
			synG_start = blast_sstart
		else:
			synG_SEQ = blastCONTIG[blast_qstart-1:blast_qend].reverse_complement()
			synG_start = blast_send
	else:
		synG_SEQ = '-'
		synG_start = 0
		blast_slen = 0
	return synG_SEQ, synG_start, blast_slen

# Set globals
DBpath = resource_filename(__name__, 'db')
blastdb = os.path.join(DBpath, 'blast', 'synG')
seroDICT = {'P':'W', 'G':'Y', 'S':'W/Y'}

# MenWY
def menwy(f, p):
	serogroup = '-'
	EX7E = '-'
	synG_RESULT = seqBLAST(f)
	synG_SEQ = synG_RESULT[0]
	synG_START = synG_RESULT[1]	
	if synG_START + synG_RESULT[2] > 945:
		start = 919 - synG_START
		EX7E_SEQ = synG_SEQ[918:945]
		EX7E = str(EX7E_SEQ.translate())
		serogroup = seroDICT[EX7E[3]]
	result = '\t'.join([f, serogroup, EX7E])
	if p:
		print(result)
	else:
		return result

def main():
	# Usage
	parser = argparse.ArgumentParser(
		formatter_class=RawTextHelpFormatter,
		description='Checks for dual W+Y antigenic specificity of Neisseria meningitidis',
		usage='\n  %(prog)s FASTA-1 FASTA-2 ... FASTA-N')
	parser.add_argument('fasta', metavar='FASTA', nargs='+', help='FASTA file to search (required)')
	parser.add_argument('--version', action='version', version=
		'=====================================\n'
		'%(prog)s v0.1\n'
		'Updated 19-Feb-2017 by Jason Kwong\n'
		'Dependencies: Python 2.x, BioPython, BLAST\n'
		'=====================================')
	args = parser.parse_args()
	
	# Main
	print('\t'.join(['SAMPLE_ID', 'W/Y', 'EX7E_MOTIF']))
	for f in args.fasta:
		menwy(f, True)
	
if __name__ == "__main__":
	main()