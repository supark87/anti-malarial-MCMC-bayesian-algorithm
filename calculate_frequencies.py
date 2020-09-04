import pandas as pd
import re
import numpy as np
import math
import statistics
from define_alleles import *
def calculate_frequencies3(genotypedata, alleles_definitions):
	ids = genotypedata.iloc[:,0].tolist()

	# retrieve the names of locus without duplicates
	col_names = list(genotypedata.columns.values)[1:]
	prev_pos = None
	locinames = {}
	lociname_index = 0
	lociname_end_index = 0
	for name in col_names:
		res = re.split('_', name)
		if prev_pos == None:
			prev_pos = res[0]
		elif prev_pos != res[0]:
			locinames[lociname_index] = (prev_pos, lociname_end_index)
			prev_pos = res[0]
			lociname_index += 1
			lociname_end_index += 1
		else:
			lociname_end_index += 1
			if (lociname_end_index == len(col_names)-1):
				locinames[lociname_index] = (prev_pos, lociname_end_index)

	nids = len(ids)
	nloci = len(locinames)

	frequencies = []
	variability = []


	n = 0
	for j in range(nloci):
		# retrieve raw alleles
		loci_name_prefix, last_index = locinames.get(j)
		raw_alleles = []
		while (n <= last_index):
			raw_alleles += genotypedata.iloc[:, n+1].tolist()
			n += 1
		raw_alleles = [loci for loci in raw_alleles if str(loci) != 'nan']

		low = alleles_definitions[j][0]
		high = alleles_definitions[j][1]

		nrows = len(alleles_definitions[j])

		sum_list = []
		sd_list = []
		for i in range(nrows):
			tf_table = []
			sum = 0
			for allele in raw_alleles:
				eval = allele > low[i] and allele <= high[i]
				tf_table.append(eval)
				if eval:
					sum += 1
			sum_list.append(sum)
			
			true_items = []
			for eval_i in range(len(tf_table)):
				if tf_table[eval_i]:
					true_items.append(raw_alleles[eval_i])

			if len(true_items) > 1:
				sd_list.append(statistics.stdev(true_items))
		sum_list = np.array(sum_list)
		frequencies.append(sum_list)
		# print(frequencies[j])
		meanSD = 0
		if (len(sd_list) > 0):
			meanSD = np.mean(sd_list)

		variability.append(meanSD)
		frequencies[j] = frequencies[j] / len(raw_alleles)

	freq_length = [len(frequencies[j]) for j in range(len(frequencies))]
	ncol = max(freq_length)
	freqmatrix = np.zeros([nloci, ncol])

	for j in range(nloci):
		for i in range(len(frequencies[j])):
			freqmatrix[j][i] = frequencies[j][i]

	ret = []
	ret.append(freq_length)
	ret.append(freqmatrix)
	ret.append(variability)
	print(ret)
	return ret

def getRawAlleles(genotypedata, locinames, j, n):
	loci_name_prefix, last_index = locinames.get(j)
	locicolumns = []
	while (n <= last_index):
		locicolumns += genotypedata.iloc[:, n+1].tolist()
		n += 1

	locicolumns = [loci for loci in locicolumns if str(loci) != 'nan']
	new_vector = np.array(locicolumns)
	return locicolumns, n


xl = pd.ExcelFile("/Users/jihwankim/Desktop/project/myworkbook.xlsx")
sheet = xl.sheet_names
# xl is the actual excel file and the sheet is the names of each sheet
# we parse only the "geno" sheet to have data
# df is the actual dataframe to use
genotypedata = xl.parse("geno")
locirepeats = [2, 2, 3, 3, 3, 3, 3]
maxk = [30, 30, 30, 30, 30, 30, 30]

alleles_definitions = define_alleles(genotypedata, locirepeats, maxk)
calculate_frequencies3(genotypedata, alleles_definitions)