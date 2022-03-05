import pandas as pd
import xml.etree.ElementTree as ET
import random

def random_score(x, frekvence=None, s=0):
	if frekvence == None:
		return random.randint(0, 7) if x == None else x
	n = random.randint(0, s - 1)
	for i, val in enumerate(frekvence):
		if n < val: return i
		n -= val
	raise ValueError

def fill_random(egmo_table, fq):
	for i in range(1, 7):
		if not fq:
			egmo_table[f"P{i}"] = egmo_table[f"P{i}"].apply(random_score)
			continue
		freqframe = egmo_table[f"P{i}"].value_counts()
		frekvence = [freqframe[i] + 1 if i in freqframe else 1 for i in range(8)]
		egmo_table[f"P{i}"] = egmo_table[f"P{i}"].apply(random_score, {"frekvence": frekvence, "s": sum(frekvence)})

def predict(df, fq):
	fill_random(df, fq)
	df["total"] = sum(df[f"P{i}"] for i in range(1, 7))
	sorted = df.sort_values("total", ascending=False)

	n = len(df.index)
	return (
		sorted.iloc[n // 2].loc['total'],
		sorted.iloc[n // 4].loc['total'],
		sorted.iloc[n // 12].loc['total']
	)

def main(fq=False):
	egmo = pd.read_csv(f"podatki/csv/egmo2.csv").set_index("code")

	for i in range(1, 7):
		egmo[f"P{i}"] = None
	egmo["prize"] = None


	tree = ET.parse('podatki/xml/test.xml')
	root = tree.getroot()

	predictions = pd.DataFrame(columns=["idx", "B", "S", "G"]).set_index("idx")

	filled = 0

	for item in root[0][::-1]:
		for x in item:
			if x.tag != "description": continue
			if "Medal" in x.text: continue
			razdeljeno = x.text.split(": ")
			naloga = razdeljeno[0][-1]
			scores = razdeljeno[1].split(", ")
			for score in scores:
				code, points = score.split(" = ")
				if(points == '?'): continue
				egmo.loc[[code], [f"P{naloga}"]] = int(points)
				row = pd.DataFrame([[filled, *predict(egmo, fq)]], columns=["idx", "B", "S", "G"]).set_index("idx")
				filled += 1
				predictions = pd.concat([predictions, row])
	
	return predictions

#egmo.loc[["BEL1"], ["P6"]] = 8
