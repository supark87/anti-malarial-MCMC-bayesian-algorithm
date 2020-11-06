import random
import math
import numpy as np
import pandas as pd
import itertools

def switch_hidden_refactor(x, nloci, maxMOI, alleles_definitions_RR, state):
	z = random.uniform(0,1)

	# Section A: If number of inferred alleles > 0
	# It will probably be more efficient to sum the two seperately, because concatenation
	# could induce memory-related performance cost, if a new memory block is being created behind the scenes.
	# inferred_allele_count = np.nansum(np.concatenate((state.hidden0[x], state.hiddenf[x])))
	inferred_allele_count = np.nansum(state.hidden0) + np.nansum(state.hiddenf)

	if (inferred_allele_count > 0):
		# removed redundant calculation
		inferred_alleles = np.where(np.concatenate((state.hidden0[x], state.hiddenf[x])) == 1)[0]

		if len(inferred_alleles) > 1:
			chosen = np.random.choice(inferred_alleles) + 1
		else:
			# This may be problematic. Check to be sure.
			chosen = inferred_alleles[0][0] + 1

		if (state.classification[x] == 0): # REINFECTION
			if chosen <= (nloci * maxMOI):
				chosenlocus = math.ceil(chosen/maxMOI)
				old = state.recoded0[x][chosen - 1].astype(np.int64)
				new = np.random.choice(np.arange(state.frequencies_RR[0][chosenlocus - 1])) + 1
				oldalleles = state.recoded0[x, np.intersect1d(np.arange(((chosenlocus - 1) * maxMOI), chosenlocus * maxMOI), np.where(state.hidden0[x] == 1)[0])]
				newallele_length = (np.mean((alleles_definitions_RR[chosenlocus - 1]["0"][new-1], alleles_definitions_RR[chosenlocus - 1]["1"][new-1])) + np.random.normal(0, state.frequencies_RR[2][chosenlocus - 1], 1))[0]
				# newallele_length = np.mean([alleles_definitions_RR[chosenlocus]["0"][new], alleles_definitions_RR[chosenlocus]["1"][new]]) + np.random.normal(0, state.frequencies_RR[2][chosenlocus], 1)
				repeatedold = state.qq
				repeatednew = state.qq

				if sum(oldalleles == old) >= 1:
					repeatedold = 1
				if sum(oldalleles == new) >= 1:
					repeatednew = 1

				numerator = sum(state.frequencies_RR[1][chosenlocus - 1][0:state.frequencies_RR[0][chosenlocus - 1]] * state.dvect[state.correction_distance_matrix[chosenlocus - 1][new - 1].astype(np.int64)]) * repeatednew
				denominator = sum(state.frequencies_RR[1][chosenlocus - 1][0:state.frequencies_RR[0][chosenlocus - 1]] * state.dvect[state.correction_distance_matrix[chosenlocus - 1][old].astype(np.int64)]) * repeatednew
				if denominator != 0:
					alpha = numerator / denominator
				else:
					alpha = 0

				if z < alpha:
					state.recoded0[x][chosen - 1] = new - 1
					newallele_length = (np.mean((alleles_definitions_RR[chosenlocus - 1]["0"][new-1], alleles_definitions_RR[chosenlocus - 1]["1"][new-1])) + np.random.normal(0, state.frequencies_RR[2][chosenlocus - 1], 1))[0]
					state.alleles0[x][chosen - 1] = newallele_length

					inputVectors = list(itertools.product(np.arange(state.MOIf[x]), np.arange(state.MOI0[x])))
					allpossiblerecrud = pd.DataFrame(inputVectors)
					order = [1, 0] # setting column's order
					allpossiblerecrud = allpossiblerecrud[[allpossiblerecrud.columns[i] for i in order]]
					allpossiblerecrud.columns = [0, 1]
					closestrecrud = np.argmin(list(map(lambda y: abs(state.alleles0[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][y]] - state.allelesf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][y]]), np.arange(0, allpossiblerecrud.shape[0]))))
					state.mindistance[x][chosenlocus - 1] = abs(state.alleles0[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][closestrecrud]] - state.allelesf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][closestrecrud]])
					state.alldistance[x][chosenlocus - 1][0:allpossiblerecrud.shape[0]] = list(map(lambda y: abs(state.alleles0[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][y]] - state.allelesf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][y]]), np.arange(0, allpossiblerecrud.shape[0])))
					state.allrecrf[x][chosenlocus - 1][0:allpossiblerecrud.shape[0]] = state.recodedf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1]]
					state.recr0[x][chosenlocus - 1] = maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][closestrecrud]
					state.recrf[x][chosenlocus - 1] = maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][closestrecrud]

			else:
				chosen = chosen - nloci * maxMOI
				chosenlocus = math.ceil(chosen/maxMOI)
				old = state.recoded0[x][chosen - 1].astype(np.int64)
				new = np.random.choice(np.arange(state.frequencies_RR[0][chosenlocus - 1])) + 1
				oldalleles = state.recoded0[x, np.intersect1d(np.arange(((chosenlocus - 1) * maxMOI), chosenlocus * maxMOI), np.where(state.hidden0[x] == 1)[0])]
				# newallele_length = np.mean([alleles_definitions_RR[chosenlocus]["0"][new], alleles_definitions_RR[chosenlocus]["1"][new]]) + np.random.normal(0, state.frequencies_RR[2][chosenlocus], 1)
				repeatedold = state.qq
				repeatednew = state.qq

				if sum(oldalleles == old) >= 1:
					repeatedold = 1
				if sum(oldalleles == new) >= 1:
					repeatednew = 1

				numerator = sum(state.frequencies_RR[1][chosenlocus - 1][0:state.frequencies_RR[0][chosenlocus - 1]] * state.dvect[state.correction_distance_matrix[chosenlocus - 1][new - 1].astype(np.int64)]) * repeatednew
				denominator = sum(state.frequencies_RR[1][chosenlocus - 1][0:state.frequencies_RR[0][chosenlocus - 1]] * state.dvect[state.correction_distance_matrix[chosenlocus - 1][old].astype(np.int64)]) * repeatednew
				alpha = numerator / denominator

				if z < alpha:
					state.recodedf[x][chosen - 1] = new - 1
					newallele_length = (np.mean((alleles_definitions_RR[chosenlocus - 1]["0"][new-1], alleles_definitions_RR[chosenlocus - 1]["1"][new-1])) + np.random.normal(0, state.frequencies_RR[2][chosenlocus - 1], 1))[0]
					state.alleles0[x][chosen - 1] = newallele_length

					inputVectors = list(itertools.product(np.arange(state.MOIf[x]), np.arange(state.MOI0[x])))
					allpossiblerecrud = pd.DataFrame(inputVectors)
					order = [1, 0] # setting column's order
					allpossiblerecrud = allpossiblerecrud[[allpossiblerecrud.columns[i] for i in order]]
					allpossiblerecrud.columns = [0, 1]
					closestrecrud = np.argmin(list(map(lambda y: abs(state.alleles0[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][y]] - state.allelesf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][y]]), np.arange(0, allpossiblerecrud.shape[0]))))
					state.mindistance[x][chosenlocus - 1] = abs(state.alleles0[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][closestrecrud]] - state.allelesf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][closestrecrud]])
					state.alldistance[x][chosenlocus - 1][0:allpossiblerecrud.shape[0]] = list(map(lambda y: abs(state.alleles0[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][y]] - state.allelesf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][y]]), np.arange(0, allpossiblerecrud.shape[0])))
					state.allrecrf[x][chosenlocus - 1][0:allpossiblerecrud.shape[0]] = state.recodedf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1]]
					state.recr0[x][chosenlocus - 1] = maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][closestrecrud]
					state.recrf[x][chosenlocus - 1] = maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][closestrecrud]

		else:
			if chosen <= (nloci * maxMOI):
				chosenlocus = math.ceil(chosen/maxMOI)
				old = state.recoded0[x][chosen - 1].astype(np.int64)
				new = np.random.choice(np.arange(state.frequencies_RR[0][chosenlocus - 1])) + 1
				oldalleles = state.recoded0[x, np.intersect1d(np.arange(((chosenlocus - 1) * maxMOI), chosenlocus * maxMOI), np.where(state.hidden0[x] == 1)[0])]
				newallele_length = (np.mean((alleles_definitions_RR[chosenlocus - 1]["0"][new-1], alleles_definitions_RR[chosenlocus - 1]["1"][new-1])) + np.random.normal(0, state.frequencies_RR[2][chosenlocus - 1], 1))[0]
				repeatedold = state.qq
				repeatednew = state.qq

				if sum(oldalleles == old) >= 1:
					repeatedold = 1
				if sum(oldalleles == new) >= 1:
					repeatednew = 1

				inputVectors = list(itertools.product(np.arange(state.MOIf[x]), np.arange(state.MOI0[x])))
				allpossiblerecrud = pd.DataFrame(inputVectors)
				order = [1, 0] # setting column's order
				allpossiblerecrud = allpossiblerecrud[[allpossiblerecrud.columns[i] for i in order]]
				allpossiblerecrud.columns = [0, 1]

				tempalleles = state.alleles0[x][maxMOI * (chosenlocus - 1): maxMOI * (chosenlocus - 1) + maxMOI]
				tempalleles[chosen - (chosenlocus - 1) * maxMOI - 1] = newallele_length
				temprecoded = state.recoded0[x][maxMOI * (chosenlocus - 1): maxMOI * (chosenlocus - 1) + maxMOI]
				temprecoded[chosen - (chosenlocus - 1) * maxMOI - 1] = new - 1

				newclosestrecrud = np.argmin(list(map(lambda y: abs(tempalleles[allpossiblerecrud[0][y]] - state.allelesf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][y]]), np.arange(0, allpossiblerecrud.shape[0]))))
				newmindistance = abs(tempalleles[allpossiblerecrud[0][newclosestrecrud]] - state.allelesf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][newclosestrecrud]])
				newalldistance = list(map(lambda y: abs(tempalleles[allpossiblerecrud[0][y]] - state.allelesf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][y]]), np.arange(0, allpossiblerecrud.shape[0])))
				newallrecrf = state.recodedf[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[1]]

				newrecr0 = maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][newclosestrecrud]
				newrecrf = maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][newclosestrecrud]


				## likelihoodnew
				likelihoodnew_numerator = state.dvect[np.round(newalldistance).astype(np.int64)]
				likelihoodnew_demominator = sum(state.frequencies_RR[1][chosenlocus - 1][0:state.frequencies_RR[0][chosenlocus - 1]] * state.dvect[state.correction_distance_matrix[chosenlocus-1][newallrecrf[0].astype(np.int64)].astype(np.int64)])
				likelihoodnew = np.nanmean(likelihoodnew_numerator / likelihoodnew_demominator) * repeatednew


				## likelihoodold
				temp = np.round(state.alldistance[x][chosenlocus - 1])
				temp = temp[np.logical_not(np.isnan(temp))].astype(np.int64)
				likelihoodold_numerator = state.dvect[temp]

				### NEED TO REVISIT
				temp_allrecrf = []
				for i in range(maxMOI * maxMOI):
					item = state.allrecrf[x][chosenlocus-1][i]
					if not np.isnan(item):
						temp_allrecrf.append(item)
				temp_allrecrf = np.asarray(temp_allrecrf).astype(np.int64)

				temp = state.frequencies_RR[1][chosenlocus - 1][0:state.frequencies_RR[0][chosenlocus - 1]] * state.dvect[state.correction_distance_matrix[chosenlocus - 1][temp_allrecrf].astype(np.int64)]
				likelihoodold_denominator = []
				for i in temp:
					likelihoodold_denominator.append(sum(i))

				likelihoodold_denominator = np.asarray(likelihoodold_denominator)

				likelihoodold = np.nanmean(likelihoodold_numerator / likelihoodold_denominator) * repeatedold

				if likelihoodnew == likelihoodold:
					alpha = 1
				else:
					if not likelihoodold == 0:
						alpha = likelihoodnew / likelihoodold
					else:
						alpha = 0

				if z < alpha:
					state.recoded0[x][chosen - 1] = new - 1
					state.alleles0[x][chosen - 1] = newallele_length
					state.mindistance[x][chosenlocus - 1] = newmindistance
					state.alldistance[x][chosenlocus - 1][0:allpossiblerecrud.shape[0]] = newalldistance
					state.allrecrf[x][chosenlocus - 1][0:allpossiblerecrud.shape[0]] = newallrecrf
					state.recr0[x][chosenlocus - 1] = maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][newclosestrecrud]
					state.recrf[x][chosenlocus - 1] = maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][newclosestrecrud]
			else:
				chosen = chosen - nloci * maxMOI
				chosenlocus = math.ceil(chosen/maxMOI)
				old = state.recoded0[x][chosen - 1].astype(np.int64)
				new = np.random.choice(np.arange(state.frequencies_RR[0][chosenlocus - 1])) + 1
				newallele_length = (np.mean((alleles_definitions_RR[chosenlocus - 1]["0"][new-1], alleles_definitions_RR[chosenlocus - 1]["1"][new-1])) + np.random.normal(0, state.frequencies_RR[2][chosenlocus - 1], 1))[0]
				oldalleles = state.recodedf[x, np.intersect1d(np.arange(((chosenlocus - 1) * maxMOI), chosenlocus * maxMOI), np.where(state.hidden0[x] == 1)[0])]
				repeatedold = state.qq
				repeatednew = state.qq

				if sum(oldalleles == old) >= 1:
					repeatedold = 1
				if sum(oldalleles == new) >= 1:
					repeatednew = 1

				inputVectors = list(itertools.product(np.arange(state.MOIf[x]), np.arange(state.MOI0[x])))
				allpossiblerecrud = pd.DataFrame(inputVectors)
				order = [1, 0] # setting column's order
				allpossiblerecrud = allpossiblerecrud[[allpossiblerecrud.columns[i] for i in order]]
				allpossiblerecrud.columns = [0, 1]

				tempalleles = state.allelesf[x][maxMOI * (chosenlocus - 1): maxMOI * (chosenlocus - 1) + maxMOI]
				tempalleles[chosen - (chosenlocus - 1) * maxMOI - 1] = newallele_length
				temprecoded = state.recodedf[x][maxMOI * (chosenlocus - 1): maxMOI * (chosenlocus - 1) + maxMOI]
				temprecoded[chosen - (chosenlocus - 1) * maxMOI - 1] = new - 1

				newclosestrecrud = np.argmin(list(map(lambda y: abs(tempalleles[allpossiblerecrud[1][y]] - state.alleles0[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][y]]), np.arange(0, allpossiblerecrud.shape[0]))))
				newmindistance = abs(tempalleles[allpossiblerecrud[1][newclosestrecrud]] - state.alleles0[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][newclosestrecrud]])
				newalldistance = list(map(lambda y: abs(tempalleles[allpossiblerecrud[1][y]] - state.alleles0[x][maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][y]]), np.arange(0, allpossiblerecrud.shape[0])))
				newallrecrf = temprecoded[allpossiblerecrud[1]]

				newrecr0 = maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][newclosestrecrud]
				newrecrf = maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][newclosestrecrud]

				## likelihoodnew
				likelihoodnew_numerator = state.dvect[np.round(newalldistance).astype(np.int64)]
				likelihoodnew_demominator = sum(state.frequencies_RR[1][chosenlocus - 1][0:state.frequencies_RR[0][chosenlocus - 1]] * state.dvect[state.correction_distance_matrix[chosenlocus-1][newallrecrf[0].astype(np.int64)].astype(np.int64)])
				likelihoodnew = np.nanmean(likelihoodnew_numerator / likelihoodnew_demominator) * repeatednew


				## likelihoodold
				temp = np.round(state.alldistance[x][chosenlocus - 1])
				temp = temp[np.logical_not(np.isnan(temp))].astype(np.int64)
				likelihoodold_numerator = state.dvect[temp]

				### NEED TO REVISIT
				temp_allrecrf = []
				for i in range(maxMOI * maxMOI):
					item = state.allrecrf[x][chosenlocus-1][i]
					if not np.isnan(item):
						temp_allrecrf.append(item)
				temp_allrecrf = np.asarray(temp_allrecrf).astype(np.int64)
				temp = state.frequencies_RR[1][chosenlocus - 1][0:state.frequencies_RR[0][chosenlocus - 1]] * state.dvect[state.correction_distance_matrix[chosenlocus - 1][temp_allrecrf].astype(np.int64)]
				likelihoodold_denominator = []
				for i in temp:
					likelihoodold_denominator.append(sum(i))
				likelihoodold_denominator = np.asarray(likelihoodold_denominator)
				likelihoodold = np.nanmean(likelihoodold_numerator / likelihoodold_denominator) * repeatedold

				if likelihoodnew == likelihoodold:
					alpha = 1
				else:
					if not likelihoodold == 0:
						alpha = likelihoodnew / likelihoodold
					else:
						alpha = 0

				if z < alpha:
					state.recoded0[x][chosen - 1] = new - 1
					state.allelesf[x][chosen - 1] = newallele_length
					state.mindistance[x][chosenlocus - 1] = newmindistance
					state.alldistance[x][chosenlocus - 1][0:allpossiblerecrud.shape[0]] = newalldistance
					state.allrecrf[x][chosenlocus - 1][0:allpossiblerecrud.shape[0]] = newallrecrf
					state.recr0[x][chosenlocus - 1] = maxMOI * (chosenlocus - 1) + allpossiblerecrud[0][newclosestrecrud]
					state.recrf[x][chosenlocus - 1] = maxMOI * (chosenlocus - 1) + allpossiblerecrud[1][newclosestrecrud]