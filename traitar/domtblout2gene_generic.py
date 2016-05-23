#!/usr/bin/env python
"""script to create a summary matrix and a gene2hmm mapping from filtered and aggregated hmmer output files"""
from PhenotypeCollection import PhenotypeCollection 
import pandas as ps
def gene2hmm(domtblout_fs, pt_models, gene2hmm_out, is_gene2hmm = False):
    """function to create a summary matrix and a gene2hmm mapping from filtered and aggregated hmmer output files"""
    #read accession file 
    accs = pt_models.get_pf2desc()
    f = open(domtblout_fs, 'r')
    domtblout_list = [i.strip() for i in f.readlines()] 
    f.close()
    sum_df = ps.DataFrame(ps.np.zeros((len(domtblout_list), accs.shape[0])))
    #set index to the actual files by getting rid of the preceding path
    sum_df.index = [i.split("/")[-1].replace("_filtered_best.dat", "") for i in domtblout_list]
    sum_df.columns = accs.index 
    #create a gene2hmm dictionary
    gene2hmm = {}  
    for f in domtblout_list:
        gene_df = ps.read_csv(f, sep = "\t")
        if not f in gene2hmm:
            gene2hmm[f] = {}
        for i in gene_df.index:
            #append genes to gene2hmm dict
            gene = gene_df.loc[i, 'target name']
            if is_gene2hmm:
                if gene not in gene2hmm[f]:
                    gene2hmm[f][gene] = [query] 
                else:
                    gene2hmm[f][gene].append(query)
            if pt_models.get_hmm_name() == "pfam":
                query = gene_df.iloc[i, 4].split('.')[0]
            if pt_models.get_hmm_name() == "dbcan":
                query = gene_df.iloc[i, 3].split('.')[0]
            #add annotations to summary file
            sum_df.loc[f.split("/")[-1].replace("_filtered_best.dat", ""), query] += 1
    #write annotation summary to disk
    sum_df.to_csv(gene2hmm_out, sep = "\t")
    #write gene2hmm to disk 
    #for i in gene2hmm:
    #    with open(gene2hmm_out, 'w') as out: 
    #        out.write("%s\t%s\n" (i, ",".join(gene2hmm[i])))
    return sum_df, gene2hmm
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("generate summary matrix from the filtered best hmmer annotation files")
    parser.add_argument("outfile", help='summary matrix output file')
    parser.add_argument("in_filtered_best_fs", help='file with filtered.best file name per row')
    parser.add_argument("archive_f", help = "phenotype archive file")
    args = parser.parse_args()
    pt_models = PhenotypeCollection(args.archive_f)
    sum_df, gene2hmm = gene2hmm(args.in_filtered_best_fs, pt_models, gene2hmm_out = args.outfile)
