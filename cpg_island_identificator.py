# python3
import argparse
from Bio import SeqIO
from Bio.Seq import Seq, MutableSeq
from Bio.Data import IUPACData
import pandas as pd
# input parameters
ap = argparse.ArgumentParser()
ap.add_argument("-in", "--input_file", required=True, help="input fasta file")
ap.add_argument("-gc", "--gc_content", required=True, help="min GC content(support for S and W nucleotides)")
ap.add_argument("-ratio", "--gc_ratio", required=True, help="min ratio of the Obs/Exp value, type = float")
ap.add_argument("-step", "--step_size", required=True, help="step size for CpG identification, type = int")
ap.add_argument("-win", "--window_size", required=True, help="window size for CpG identification, type = int")
ap.add_argument("-out", "--output_file", required=True, help="output txt file")
args = vars(ap.parse_args())
# calculate obs value
def obs(seq):
  return seq.count('CG')
# calculate Exp value
def exp(seq):
  return round(seq.count('C') * seq.count('G') / int(args['window_size']), 2)
# calculate gc content
def gc_content(seq):
    gc = sum(seq.count(x) for x in ["G", "C", "S"])
    return round(gc * 100 / sum(seq.count(x) for x in ["A", "T", "G", "C", "S", "W"]), 2)
# main
gcobs = []
gcexp = []
headers = [] # setup empty lists
for record in SeqIO.parse(args['input_file'], "fasta"):
    for i in range(0, len(record.seq) - int(args['window_size']) + 1, int(args['step_size'])):
        if gc_content(record.seq[i:i + int(args['window_size'])]) > float(args['gc_content']):
           gcobs.append(obs(record.seq[i:i + int(args['window_size'])]))
           gcexp.append(exp(record.seq[i:i + int(args['window_size'])]))
           headers.append(i)
# create data frame
df = pd.DataFrame()
df['start'] = headers
df['obs'] = gcobs
df['exp'] = gcexp
df['obs/exp'] = round(df['obs']/df['exp'], 2)
df = df[df['exp'] > 0]
df = df[df['obs/exp'] > float(args['gc_ratio'])]
df = df.sort_values(by=['obs/exp'], ascending=False)
start = df.iloc[:,0]
end = start.astype(int) + int(args['window_size'])
df1 = pd.DataFrame()
df1['start'] = start
df1['end'] = end
df1['obs'] = df[["obs"]]
df1['exp'] = df[["exp"]]
df1['obs/exp'] = df[["obs/exp"]]
# export
with open(args['output_file'], 'a') as f:
    f.write(
        df1.to_csv(header = True, index = False, sep = '\t', doublequote= False, line_terminator= '\n')
    )

