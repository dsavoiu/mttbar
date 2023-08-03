import sys
import pickle
import hist
import awkward as ak
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

signalnames = {"zprime_tt", "hpseudo_tt", "hscalar_tt", "rsgluon_tt", "tt"}
already_processed_producer = set()
had_colors = ["yellow", "orange", "red", "purple", "blue", "olive", "darkgreen", "dimgrey", "black"]

data_sig = {}
data_back = {}

for data in (data_sig, data_back):
    data["all"] = {"producer_name":[], "n_jet_max":[], "eff_back":[], "had_color":[]}
    data["best"] = {"producer_name":[], "n_jet_max":[], "eff_back":[], "had_color":[], "add":{}}
    data["worst"] = {"producer_name":[], "n_jet_max":[], "eff_back":[], "had_color":[], "add":{}}
    data["already_considered_n_jet_max"] = set() #i

    for n_jet_max in range(2, 10 + 1):
        data["best"]["add"].update({f"producer_name_{n_jet_max}":"", f"n_jet_max_{n_jet_max}":0,
        f"eff_back_{n_jet_max}":0, f"had_color_{n_jet_max}":""})
        data["worst"]["add"].update({f"producer_name_{n_jet_max}":"", f"n_jet_max_{n_jet_max}":0, f"eff_back_{n_jet_max}":1, f"had_color_{n_jet_max}":""})

data_sig["label"] = "efficiency"
data_sig["color"] = "r"
data_back["label"] = "background rejection"
data_back["color"] = "b"

# Iterate over producer names.

for i in range(1, len(sys.argv)):
    path = sys.argv[i]
    path_split = path.split("/")
    producer_name = path_split[-3]

    if producer_name not in already_processed_producer:
        already_processed_producer.add(producer_name)

        producer_first_split = producer_name.split("__")
        n_jet_max = int(producer_first_split[1].split("x")[1])
        producer_h_split = producer_first_split[2].split("h")
        producer_h_split_split = producer_h_split[1].split("_")
        n_jet_had_min = int(producer_h_split_split[0])
        n_jet_had_max = int(producer_h_split_split[1])
        producer_l_split = producer_first_split[3].split("l")
        producer_l_split_split = producer_l_split[1].split("_")
        n_jet_lep_min = int(producer_l_split_split[0])
        n_jet_lep_max = int(producer_l_split_split[1])
        
        numerator = 0
        denominator = 0
        eff_back = 0

# Interate over all datasets for one producer.

        for j in range(1, len(sys.argv)):

            if producer_name in sys.argv[j]:

                dataset = sys.argv[j].split("/")[-7]
                is_signal = any(dataset.startswith(prefix) for prefix in signalnames)
                arr = ak.from_parquet(sys.argv[j])

                if is_signal:
                    data = data_sig
                    chi2_cut = arr.TTbar.chi2 < 30
                else:
                    data = data_back
                    chi2_cut = arr.TTbar.chi2 > 30

                denominator += len(arr)
                numerator += sum(chi2_cut)

        eff_back = numerator/denominator
        print(producer_name, eff_back)

        for data in (data_sig, data_back):

            data["all"]["producer_name"].append(producer_name)
            data["all"]["n_jet_max"].append(n_jet_max)
            data["all"]["eff_back"].append(eff_back)
            data["all"]["had_color"].append(had_colors[n_jet_had_max - 1])

            if n_jet_max not in data["already_considered_n_jet_max"]:
                data["already_considered_n_jet_max"].add(n_jet_max)
                data["best"]["add"][f"n_jet_max_{n_jet_max}"] = n_jet_max
                data["worst"]["add"][f"n_jet_max_{n_jet_max}"] = n_jet_max

            if eff_back > data["best"]["add"][f"eff_back_{n_jet_max}"]:
                data["best"]["add"][f"producer_name_{n_jet_max}"] = producer_name
                data["best"]["add"][f"eff_back_{n_jet_max}"] = eff_back
                data["best"]["add"][f"had_color_{n_jet_max}"] = had_colors[n_jet_had_max - 1]

            if eff_back <= data["worst"]["add"][f"eff_back_{n_jet_max}"]:
                data["worst"]["add"][f"producer_name_{n_jet_max}"] = producer_name
                data["worst"]["add"][f"eff_back_{n_jet_max}"] = eff_back
                data["worst"]["add"][f"had_color_{n_jet_max}"] = had_colors[n_jet_had_max - 1]

for data in (data_sig, data_back):
    for extrem in ("best", "worst"):
        print(extrem)
        for n_jet_max in range(2, 10 + 1):
            if data[f"{extrem}"]["add"][f"n_jet_max_{n_jet_max}"] != 0:
                data[f"{extrem}"]["producer_name"].append(data[f"{extrem}"]["add"][f"producer_name_{n_jet_max}"])
                data[f"{extrem}"]["n_jet_max"].append(data[f"{extrem}"]["add"][f"n_jet_max_{n_jet_max}"])
                data[f"{extrem}"]["eff_back"].append(data[f"{extrem}"]["add"][f"eff_back_{n_jet_max}"])
                data[f"{extrem}"]["had_color"].append(data[f"{extrem}"]["add"][f"had_color_{n_jet_max}"])
# print(data_sig["worst"]["add"][f"had_color_2"], data_sig["worst"]["had_color"])
#--------------------------------------------------------------------------------------------------

# Plot efficiency/ background rejection for best parameters.

for data in (data_sig, data_back):

    plt.scatter(data["best"]["n_jet_max"], data["best"]["eff_back"],label=data["label"],color=data["color"], marker="o")

    plt.xlabel("n_jet_max")
    plt.ylabel("efficieny/background rejection")
    plt.savefig(f"/nfs/dust/cms/user/schroede/mttbar/plots/efficiencies/n_jet_max_best_zprime_tt_m3000_w300_madgraph_without_x10_h1_8__l1_6_7__h1_9__l1_1.pdf")

# Plot efficiency for all n_jet_had_max choices.

fig1,ax1 = plt.subplots()

scatter_grey = ax1.scatter(data_sig["all"]["n_jet_max"], data_sig["all"]["eff_back"], c="grey", marker="_")
scatter_max = ax1.scatter(data_sig["best"]["n_jet_max"], data_sig["best"]["eff_back"], c=data_sig["best"]["had_color"], marker="^")
scatter_min = ax1.scatter(data_sig["worst"]["n_jet_max"], data_sig["worst"]["eff_back"], c=data_sig["worst"]["had_color"], marker="v")
plt.xlabel("n_jet_max")
plt.ylabel("efficiency")
plt.savefig("/nfs/dust/cms/user/schroede/mttbar/plots/efficiency_n_jet_had_min_max_zprime_tt_m3000_w300_madgraph_without_x10_h1_8__l1_6_7__h1_9__l1_1.pdf")

plt.figure()
scatter = plt.scatter(data_sig["all"]["n_jet_max"], data_sig["all"]["eff_back"], c=data_sig["all"]["had_color"], marker="o")
plt.xlabel("n_jet_max")
plt.ylabel("efficiency")

yellow_dot = mpatches.Patch(color="yellow", hatch="o", label="1")
orange_dot = mpatches.Patch(color="orange", hatch="o", label="2")
red_dot = mpatches.Patch(color="red", hatch="o", label="3")
purple_dot = mpatches.Patch(color="purple", hatch="o", label="4")
blue_dot = mpatches.Patch(color="blue", hatch="o", label="5")
olive_dot = mpatches.Patch(color="olive", hatch="o", label="6")
darkgreen_dot = mpatches.Patch(color="darkgreen", hatch="o", label="7")
dimgrey_dot = mpatches.Patch(color="dimgrey", hatch="o", label="8")
black_dot = mpatches.Patch(color="black", hatch="o", label="9")
plt.legend(handles=[yellow_dot,
    orange_dot,
    red_dot,
    purple_dot,
    blue_dot,
    olive_dot,
    darkgreen_dot,
    dimgrey_dot,
    black_dot,
    ],
    title="Maximum number of hadronic jets")
plt.savefig("/nfs/dust/cms/user/schroede/mttbar/plots/efficiency_n_jet_had_all_zprime_tt_m3000_w300_madgraph_without_x10_h1_8__l1_6_7__h1_9__l1_1.pdf")

plt.figure()
scatter_best = plt.scatter(data_sig["best"]["n_jet_max"],
    data_sig["best"]["eff_back"],
    label=data_sig["label"],
    color=data_sig["best"]["had_color"],
    marker="o",
    )
plt.savefig("/nfs/dust/cms/user/schroede/mttbar/plots/efficiency_n_jet_had_best_zprime_tt_m3000_w300_madgraph_without_x10_h1_8__l1_6_7__h1_9__l1_1.pdf")

plt.figure()
scatter_zoom = plt.scatter(data_sig["all"]["n_jet_max"], data_sig["all"]["eff_back"], c=data_sig["all"]["had_color"], marker="o")
plt.ylim(0.82, 0.85)
plt.savefig(f"/nfs/dust/cms/user/schroede/mttbar/plots/efficiency_n_jet_had_all_zoom_zprime_tt_m3000_w300_madgraph_without_x10_h1_8__l1_6_7__h1_9__l1_1.pdf")

plt.figure()
scatter_zoom2 = plt.scatter(data_sig["all"]["n_jet_max"], data_sig["all"]["eff_back"], c=data_sig["all"]["had_color"], marker="o")
plt.ylim(0.84, 0.845)
plt.savefig(f"/nfs/dust/cms/user/schroede/mttbar/plots/efficiency_n_jet_had_all_zoom2_zprime_tt_m3000_w300_madgraph_without_x10_h1_8__l1_6_7__h1_9__l1_1.pdf")

plt.figure()
scatter_zoom3 = plt.scatter(data_sig["all"]["n_jet_max"], data_sig["all"]["eff_back"], c=data_sig["all"]["had_color"], marker="o")
plt.ylim(0.8425, 0.8432)
plt.savefig(f"/nfs/dust/cms/user/schroede/mttbar/plots/efficiency_n_jet_had_all_zoom3_zprime_tt_m3000_w300_madgraph_without_x10_h1_8__l1_6_7__h1_9__l1_1.pdf")
    

# Plot rock curve

#plt.figure()
#plt.plot(data_back["best"]["eff_back"], data_sig["best"]["eff_back"])
#plt.xlabel("background_rejection")
#plt.ylabel("efficiency")
#plt.savefig(f"/nfs/dust/cms/user/schroede/mtt/plots/rock_curve/{producer_names_sig_str}_{producer_names_back_str}")
