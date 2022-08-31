import pandas as pd
import xml.etree.ElementTree as ET
import random
import multiprocessing

pd.options.mode.chained_assignment = None

def random_score(x, frekvence=None, s=0):
    if x != None: return x
    if frekvence == None:
        return random.randint(0, 7)
    n = random.randint(0, s - 1)
    for i, val in enumerate(frekvence):
        if n < val:
            return i
        n -= val
    raise ValueError


def fill_fixed(df, n):
    for i in range(1, 7):
        df[f"P{i}"] = df[f"P{i}"].fillna(n)


def fill_random(egmo_table, n, fq):
    for i in range(1, 7):
        if not fq:
            egmo_table[f"P{i}"] = egmo_table[f"P{i}"].apply(random_score)
            continue
        freqframe = (egmo_table[egmo_table['official']])[f"P{i}"].value_counts()
        previous_egmo = pd.read_csv(f"podatki/csv/egmo{n-1}.csv").set_index("code")
        previous_egmo = previous_egmo[previous_egmo['official']]
        previous_freqframe = (previous_egmo[previous_egmo['official']])[f"P{i}"].value_counts()
        frekvence = [
            1 + 
            freqframe[i] if i in freqframe else 0 +
            previous_freqframe[i] if i in previous_freqframe else 0
            for i in range(8)]
        egmo_table[f"P{i}"] = egmo_table[f"P{i}"].apply(
            random_score, {"frekvence": frekvence, "s": sum(frekvence)})


def fill_smart(egmo_table, n, country_codes, weights):
    
    for i in range(1, 7):
        freqframe = (egmo_table[egmo_table['official']])[f"P{i}"].value_counts()
        previous_egmo = pd.read_csv(f"podatki/csv/egmo{n-1}.csv").set_index("code")
        previous_egmo = previous_egmo[previous_egmo['official']]
        previous_freqframe = (previous_egmo[previous_egmo['official']])[f"P{i}"].value_counts()

        frekvence = [
            1 + 
            freqframe[i] if i in freqframe else 0 +
            previous_freqframe[i] if i in previous_freqframe else 0
            for i in range(8)]
        
        vsota = sum(frekvence)
        frekvence = [x * len(country_codes) / vsota for x in frekvence]
        egmo_table['weight'] = egmo_table.index.str[0:3].map(weights)
        egmo_table[f"P{i}"] = egmo_table.apply(lambda x: freqscore(x[f"P{i}"], x['weight'], frekvence), axis=1)


def freqscore(x, weight, frekvence=None):
    if x != None: return x
    if frekvence == None:
        return random.randint(0, 7)
    for i, val in enumerate(frekvence):
        if weight < val:
            return i
        weight -= val
    raise ValueError


def predict(df, n, fq=None, cond="likely", country_codes=None, weights=None):
    if cond == "min":
        fill_fixed(df, 0)
    elif cond == "max":
        fill_fixed(df, 7)
    elif cond == "random":
        if n < 3:
            print("Ti parametri so na voljo le od tretjega EGMO dalje!")
            return
        fill_random(df, n, fq)
    elif cond == "likely":
        if n < 3:
            print("Ti parametri so na voljo le od tretjega EGMO dalje!")
            return
        fill_smart(df, n, country_codes, weights)
    else:
        raise ValueError("Parameter 'cond' je neveljaven!")
    df["total"] = sum(df[f"P{i}"] for i in range(1, 7))
    urejeni = df.sort_values("total", ascending=False)

    urejeni = urejeni[urejeni['official']]

    n = len(urejeni.index)

    first_cut = urejeni.iloc[n // 2].loc['total']

    scores = urejeni['total'][::-1]

    cutoffs = []
    for bronze in [first_cut, first_cut + 1]:
        bronze_count =  n - scores.searchsorted(bronze, side='left')
        second_cut = urejeni.iloc[bronze_count // 2].loc['total']
        for silver in [second_cut, second_cut + 1]:
            silver_count = n - scores.searchsorted(silver, side='left')
            third_cut = urejeni.iloc[silver_count // 3].loc['total']
            for gold in [third_cut, third_cut + 1]:
                cutoffs.append((bronze, silver, gold))


    if cond == "random" or cond == "likely":
        error = 99999
        opt = (0, 0, 0)
        for (bronze, silver, gold) in cutoffs:
            bronze_num = n - scores.searchsorted(bronze, side='left')
            silver_num = n - scores.searchsorted(silver, side='left')
            gold_num = n - scores.searchsorted(gold, side='left')
            current_error = (
                (abs((n + 1) / (bronze_num + 1) - 2) + 1) *
                (abs((bronze_num + 1) / (silver_num - gold_num + 1) - 3 / 2) + 1) *
                (abs((silver_num + 1) / (gold_num + 1) - 3) + 1)
            )
            if current_error < error:
                error, opt = current_error, (bronze, silver, gold)

        return opt

    if cond == "min":
        return cutoffs[0]

    if cond == "max":
        return cutoffs[-1]


def main(n, fq=True, cond="likely"):

    egmo = pd.read_csv(f"podatki/csv/egmo{n}.csv").set_index("code")

    country_codes = list(set(x[:3] for x in egmo.index))
    averages = {}
    for country in country_codes:
        placement = []
        for i in range(2, n):
            current_egmo = pd.read_csv(f"podatki/csv/egmo{i}.csv")
            current_egmo = current_egmo[current_egmo['official']]
            current_egmo['code'] = current_egmo['code'].str[:3]
            by_countries = current_egmo.groupby(['code']).sum()
            by_countries['total'] = by_countries.iloc[:,1:7].sum(axis=1)
            by_countries = by_countries.sort_values(['total'], ascending=False)
            try:
                placement.append(by_countries.index.get_loc(country))
            except KeyError:
                continue
        averages[country] = sum(placement) / len(placement) if placement != [] else 1000
    country_codes.sort(key=lambda x: -averages[x])
    weights = {}
    for i, code in enumerate(country_codes):
        weights[code] = i

    for i in range(1, 7):
        egmo[f"P{i}"] = None
    egmo["prize"] = None

    tree = ET.parse(f'podatki/xml/egmo{n}.xml')
    root = tree.getroot()

    predictions = pd.DataFrame(columns=["idx", "B", "S", "G", "Actual B", "Actual S", "Actual G"]).set_index("idx")

    filled = 0

    cutoffs = []
    with open("podatki/csv/cutoffs.csv") as ctf:
        all = ctf.readlines()
        cutoffs = tuple([int(x) for x in all[n-1].rstrip().split(',')[:0:-1]])

    for item in root[0][::-1]:
        for x in item:
            if x.tag != "description":
                continue
            if "Medal" in x.text:
                continue
            razdeljeno = x.text.split(": ")
            naloga = razdeljeno[0][-1]
            scores = razdeljeno[1].split(", ")
            for score in scores:
                code, points = score.split(" = ")
                if(points == '?'):
                    continue
                egmo.loc[[code], [f"P{naloga}"]] = int(points)
                if not egmo.loc[code, "official"]:
                    continue
                row = pd.DataFrame([[filled, *predict(egmo[egmo["official"]], n, fq, cond, country_codes, weights), *cutoffs]],
                                   columns=["idx", "B", "S", "G", "Actual B", "Actual S", "Actual G"]).set_index("idx")

                filled += 1
                predictions = pd.concat([predictions, row])

    return predictions

if __name__ == "__main__":
    main(11, fq=False, cond="random")
