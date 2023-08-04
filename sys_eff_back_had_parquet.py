import sys
import pickle
import hist
import awkward as ak
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

signalnames = {"zprime_tt", "hpseudo_tt", "hscalar_tt", "rsgluon_tt", "tt"}
already_processed_producer = set()
had_colors = ["darkorange", "red", "purple", "blue", "olive", "darkgreen", "saddlebrown", "dimgrey", "black"]

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
        for n_jet_max in range(2, 10 + 1):
            if data[f"{extrem}"]["add"][f"n_jet_max_{n_jet_max}"] != 0:
                data[f"{extrem}"]["producer_name"].append(data[f"{extrem}"]["add"][f"producer_name_{n_jet_max}"])
                data[f"{extrem}"]["n_jet_max"].append(data[f"{extrem}"]["add"][f"n_jet_max_{n_jet_max}"])
                data[f"{extrem}"]["eff_back"].append(data[f"{extrem}"]["add"][f"eff_back_{n_jet_max}"])
                data[f"{extrem}"]["had_color"].append(data[f"{extrem}"]["add"][f"had_color_{n_jet_max}"])

#--------------------------------------------------------------------------------------------------

# Produce legend entries.

orange_dot = mpatches.Patch(color="orange", hatch="o", label="1")
red_dot = mpatches.Patch(color="red", hatch="o", label="2")
purple_dot = mpatches.Patch(color="purple", hatch="o", label="3")
blue_dot = mpatches.Patch(color="blue", hatch="o", label="4")
olive_dot = mpatches.Patch(color="olive", hatch="o", label="5")
darkgreen_dot = mpatches.Patch(color="darkgreen", hatch="o", label="6")
saddlebrown_dot = mpatches.Patch(color="saddlebrown", hatch="o", label="7")
dimgrey_dot = mpatches.Patch(color="dimgrey", hatch="o", label="8")
black_dot = mpatches.Patch(color="black", hatch="o", label="9")

# Plot efficiency for all n_jet_had_max choices.

fig_all,ax_all = plt.subplots()
scatter_all = ax_all.scatter(data_sig["all"]["n_jet_max"], data_sig["all"]["eff_back"], c=data_sig["all"]["had_color"], marker = "o")
plt.xlabel("n_jet_max")
plt.ylabel("efficiency")
plt.title("Reconstruction efficiency dependence on \n considered number of total and hadronic jets")

box_all = ax_all.get_position()
ax_all.set_position([box_all.x0, box_all.y0, box_all.width * 0.8, box_all.height])

ax_all_zoom = fig_all.add_axes([0.45, 0.17, 0.25, 0.2])
scatter_all_zoom = ax_all_zoom.scatter(data_sig["all"]["n_jet_max"], data_sig["all"]["eff_back"], c=data_sig["all"]["had_color"], marker = "o")
plt.xlim(5.5, 10.5)
plt.ylim(0.82, 0.85)

ax_all.legend(handles=[
    orange_dot,
    red_dot,
    purple_dot,
    blue_dot,
    olive_dot,
    darkgreen_dot,
    saddlebrown_dot,
    dimgrey_dot,
    black_dot,
    ],
    title='Maximum number \n of hadronic jets',
    loc='upper left', 
    bbox_to_anchor=(1, 1),
    )
plt.savefig("/nfs/dust/cms/user/schroede/mttbar/plots/efficiency_n_jet_had_all_zprime_tt_m3000_w300_madgraph_without_x10_h1_8__l1_6_7__h1_9__l1_1.pdf")

# Plot efficiency for all n_jet_had_max choices, highlighting best and worst.

fig_extrem,ax_extrem = plt.subplots()

scatter_grey = ax_extrem.scatter(data_sig["all"]["n_jet_max"], data_sig["all"]["eff_back"], c="grey", marker = "_")
scatter_max = ax_extrem.scatter(data_sig["best"]["n_jet_max"], data_sig["best"]["eff_back"], c=data_sig["best"]["had_color"], marker = "^")
scatter_min = ax_extrem.scatter(data_sig["worst"]["n_jet_max"], data_sig["worst"]["eff_back"], c=data_sig["worst"]["had_color"], marker = "v")
plt.xlabel("n_jet_max")
plt.ylabel("efficiency")
plt.title("Best and worst reconstruction efficiency \n for considered number of total and hadronic jets")

box_extrem = ax_extrem.get_position()
ax_extrem.set_position([box_extrem.x0, box_extrem.y0, box_extrem.width * 0.8, box_extrem.height])

ax_extrem_zoom = fig_extrem.add_axes([0.45, 0.17, 0.25, 0.2])
scatter_grey_zoom = ax_extrem_zoom.scatter(data_sig["all"]["n_jet_max"], data_sig["all"]["eff_back"], c="grey", marker = "_")
scatter_max_zoom = ax_extrem_zoom.scatter(data_sig["best"]["n_jet_max"], data_sig["best"]["eff_back"], c=data_sig["best"]["had_color"], marker = "^")
scatter_min_zoom = ax_extrem_zoom.scatter(data_sig["worst"]["n_jet_max"], data_sig["worst"]["eff_back"], c=data_sig["worst"]["had_color"], marker = "v")
plt.xlim(5.5, 10.5)
plt.ylim(0.82, 0.85)

ax_extrem.legend(handles=[
    orange_dot,
    red_dot,
    purple_dot,
    blue_dot,
    olive_dot,
    darkgreen_dot,
    saddlebrown_dot,
    dimgrey_dot,
    black_dot,
    ],
    title='Maximum number \n of hadronic jets',
    loc='upper left',
    bbox_to_anchor=(1, 1),
    )


plt.savefig("/nfs/dust/cms/user/schroede/mttbar/plots/efficiency_n_jet_had_extrem_zprime_tt_m3000_w300_madgraph_without_x10_h1_8__l1_6_7__h1_9__l1_1.pdf")


# Plot efficiency/ background rejection for best parameters.

for data in (data_sig, data_back):

    fig_best,ax_best = plt.subplots()

    ax_best.scatter(data["best"]["n_jet_max"], data["best"]["eff_back"],label=data["label"],color=data["best"]["had_color"], marker="o")

    plt.xlabel("n_jet_max")
    plt.ylabel("efficieny/background rejection")
    plt.title("Best reconstruction efficiency \n for considered number of total and hadronic jets")

    box_best = ax_best.get_position()
    ax_best.set_position([box_best.x0, box_best.y0, box_best.width * 0.8, box_best.height])

    ax_best_zoom = fig_best.add_axes([0.35, 0.17, 0.35, 0.4])
    scatter_best_zoom = ax_best_zoom.scatter(data["best"]["n_jet_max"], data["best"]["eff_back"],label=data["label"],color=data["color"], marker="o")
    plt.xlim(5.5, 10.5)
    plt.ylim(0.82, 0.85)

    ax_best.legend(handles=[
        orange_dot,
        red_dot,
        purple_dot,
        blue_dot,
        olive_dot,
        darkgreen_dot,
        saddlebrown_dot,
        dimgrey_dot,
        black_dot,
        ],
        title='Maximum number \n of hadronic jets',
        loc='upper left',
        bbox_to_anchor=(1, 1),
        )

plt.savefig(f"/nfs/dust/cms/user/schroede/mttbar/plots/efficiency_n_jet_had_best_zprime_tt_m3000_w300_madgraph_without_x10_h1_8__l1_6_7__h1_9__l1_1.pdf")


# Plot rock curve

#plt.figure()
#plt.plot(data_back["best"]["eff_back"], data_sig["best"]["eff_back"])
#plt.xlabel("background_rejection")
#plt.ylabel("efficiency")
#plt.savefig(f"/nfs/dust/cms/user/schroede/mtt/plots/rock_curve/{producer_names_sig_str}_{producer_names_back_str}")
