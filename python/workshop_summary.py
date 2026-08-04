#!/usr/bin/env python3

import os
import re
from datetime import date

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import pycountry

REDASH_QUERY_125 = "https://redash.carpentries.org/api/queries/125/results.csv?api_key=ef7xp02JqDvg7JkEbxbElfg8ICgBaQEaXnz0NhQS"
NATURAL_EARTH_COUNTRIES = "lib/ne_50m_admin_0_countries.zip"
WORKSHOP_TYPES = {
    "SWC": "Software Carpentry",
    "DC": "Data Carpentry",
    "LC": "Library Carpentry",
    "TTT": "Instructor Training",
    "HPCC": "HPC Carpentry",
    "AIC": "AI Carpentry",
    "Circuits": "Mix & Match"
}

def check_for_na(dataframe, column):
    if dataframe[column].isna().any():
        raise ValueError("found NAs, is there a new workshop type?")
    return dataframe


def check_export_dir(file_path):
    directory = os.path.dirname(file_path)
    if directory and (not os.path.isdir(directory)):
        raise FileNotFoundError(
            f"directory: {directory} doesn't exist. Create it before using this function."
        )


def write_figure(fig, outfile):
    """
    Save matplotlib figure directly to SVG or wrap it in simple HTML.
    """
    if outfile.endswith(".svg"):
        fig.savefig(outfile, format="svg")
        return outfile

    if outfile.endswith(".html"):
        svg_path = outfile.replace(".html", ".svg")
        fig.savefig(svg_path, format="svg")

        svg_name = os.path.basename(svg_path)
        html = (
            "<!doctype html>\n"
            "<html><head><meta charset=\"utf-8\"></head><body "
            "style=\"margin:0;background:#ffffff;\">\n"
            f"<img src=\"/{svg_name}\" style=\"width:100%;height:auto;display:block;\" "
            "alt=\"workshop summary plot\">\n"
            "</body></html>\n"
        )
        with open(outfile, "w") as html_file:
            html_file.write(html)
        return outfile

    raise ValueError(f"Unsupported output extension for {outfile}")


def get_workshop_type(tag_name):
    tags = [tag.strip() for tag in str(tag_name).split(",")]
    for tag in tags:
        if tag in WORKSHOP_TYPES:
            return WORKSHOP_TYPES[tag]
    return None


def get_country_name(iso2_code):
    try:
        country = pycountry.countries.get(alpha_2=iso2_code)
        return country.name if country else None
    except Exception:
        return None


def get_country_iso3(iso2_code):
    try:
        country = pycountry.countries.get(alpha_2=iso2_code)
        return country.alpha_3 if country else None
    except Exception:
        return None


def prepare_workshops_through_time(wksp_data):
    summary_by_type = wksp_data.copy()
    summary_by_type["tag_name"] = summary_by_type["tag_name"].apply(get_workshop_type)
    summary_by_type = (
        summary_by_type.groupby(["tag_name", "end_date"], as_index=False)
        .size()
        .rename(columns={"size": "n"})
    )

    summary_total = (
        wksp_data.groupby("end_date", as_index=False)
        .size()
        .rename(columns={"size": "n"})
    )
    summary_total["tag_name"] = "Total"

    summary = pd.concat([summary_by_type, summary_total], ignore_index=True)
    summary = check_for_na(summary, "tag_name")
    summary = summary.sort_values(["tag_name", "end_date"])
    summary["n_total"] = summary.groupby("tag_name")["n"].cumsum()

    return summary


def workshops_through_time(wksp_data, outfile="_images/plot_workshops_through_time.html"):
    check_export_dir(outfile)
    summary = prepare_workshops_through_time(wksp_data)

    fig, ax = plt.subplots(figsize=(1600 / 72, 900 / 72), dpi=72)
    for tag_name, group in summary.groupby("tag_name"):
        group = group.sort_values("end_date")
        ax.plot(group["end_date"], group["n_total"], label=tag_name, linewidth=2)

    ax.set_title("Number of workshops through time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Workshops")
    ax.legend(title="Workshop type")
    fig.autofmt_xdate()
    fig.tight_layout()

    write_figure(fig, outfile)
    plt.close(fig)
    return outfile


def workshops_by_year(wksp_data, outfile="_images/plot_workshops_by_year.html"):
    check_export_dir(outfile)

    summary_per_year = prepare_workshops_through_time(wksp_data).copy()
    summary_per_year["year"] = summary_per_year["end_date"].dt.strftime("%Y")
    summary_per_year = (
        summary_per_year.groupby(["year", "tag_name"], as_index=False)["n"].sum()
    )

    all_years = sorted(summary_per_year["year"].unique())
    all_types = sorted(summary_per_year["tag_name"].unique())
    complete_index = pd.MultiIndex.from_product(
        [all_years, all_types], names=["year", "tag_name"]
    )
    summary_per_year = (
        summary_per_year.set_index(["year", "tag_name"])
        .reindex(complete_index, fill_value=0)
        .reset_index()
    )

    years = sorted(summary_per_year["year"].unique())
    tags = sorted(summary_per_year["tag_name"].unique())
    width = 0.8 / max(len(tags), 1)
    x_positions = list(range(len(years)))

    fig, ax = plt.subplots(figsize=(1600 / 72, 900 / 72), dpi=72)

    for idx, tag in enumerate(tags):
        values = []
        for year in years:
            value = summary_per_year[
                (summary_per_year["year"] == year) & (summary_per_year["tag_name"] == tag)
            ]["n"].sum()
            values.append(value)

        offset = (idx - (len(tags) - 1) / 2) * width
        positions = [x + offset for x in x_positions]
        ax.bar(positions, values, width=width, label=tag)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(years, rotation=45, ha="right")
    ax.set_title("Number of workshops per year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Workshops")
    ax.legend(title="Workshop type")
    fig.tight_layout()

    write_figure(fig, outfile)
    plt.close(fig)
    return outfile


def workshops_map(wksp_data, outfile="_images/plot_workshops_map.svg"):
    check_export_dir(outfile)

    wksp_data = wksp_data.copy()
    wksp_data = wksp_data[
        (wksp_data["latitude"] < 90)
        & ~((wksp_data["latitude"] == 0) & (wksp_data["longitude"] == 0)) # online workshops
        & ~((wksp_data["latitude"] == 45) & (wksp_data["longitude"] == -1)) # default template values
        & ~(
            (wksp_data["latitude"].between(-49.0, -48.8)) &
            (wksp_data["longitude"].between(-123.1, -122.9))
        )
    ]

    wksp_data_no_online = wksp_data[wksp_data["country"] != "W3"].copy()
    wksp_data_no_online["iso_a3"] = wksp_data_no_online["country"].apply(get_country_iso3)
    wksp_data_no_online = wksp_data_no_online.dropna(subset=["iso_a3"])

    wksp_map_points = wksp_data_no_online.copy()
    wksp_map_points["latitude"] = (wksp_map_points["latitude"] / 0.5).round() * 0.5
    wksp_map_points["longitude"] = (wksp_map_points["longitude"] / 0.5).round() * 0.5
    wksp_map_points = (
        wksp_map_points.groupby(["latitude", "longitude"], as_index=False)
        .size()
        .rename(columns={"size": "n_loc"})
    )

    summ_by_country = (
        wksp_data_no_online.groupby("iso_a3", as_index=False)
        .size()
        .rename(columns={"size": "n"})
    )

    world = gpd.read_file(NATURAL_EARTH_COUNTRIES)
    # Prefer ADM0_A3 over ISO_A3
    if "ADM0_A3" in world.columns:
        iso_col = "ADM0_A3"
    elif "ISO_A3" in world.columns:
        iso_col = "ISO_A3"
    else:
        raise RuntimeError("Could not find ISO A3 column in Natural Earth dataset.")

    world = world[[iso_col, "geometry"]].copy().rename(columns={iso_col: "iso_a3"})
    world = world.merge(summ_by_country, on="iso_a3", how="left")

    fig, ax = plt.subplots(figsize=(1600 / 72, 900 / 72), dpi=72)
    fig.patch.set_facecolor("#f1feff")
    ax.set_facecolor("#f1feff")

    world.plot(ax=ax, color="#cccccc", edgecolor="white", linewidth=0.2)

    world_with_data = world[world["n"].notna()].copy()
    if not world_with_data.empty:
        world_with_data["n_capped"] = world_with_data["n"].clip(lower=1, upper=500)
        norm = mcolors.LogNorm(vmin=1, vmax=500)
        world_with_data.plot(
            ax=ax,
            column="n_capped",
            cmap="viridis",
            norm=norm,
            edgecolor="white",
            linewidth=0.2,
            legend=False,
        )

        color_ticks = [1, 10, 100, 500]

        scalar_mappable = plt.cm.ScalarMappable(norm=norm, cmap="viridis")
        scalar_mappable.set_array([])
        colorbar = fig.colorbar(
            scalar_mappable,
            ax=ax,
            orientation="horizontal",
            fraction=0.03,
            pad=0.03,
            shrink=0.7,
        )
        colorbar.set_label("Number of Workshops")
        colorbar.set_ticks(color_ticks)
        colorbar.set_ticklabels([str(tick) for tick in color_ticks])

    marker_size = wksp_map_points["n_loc"].pow(0.5) * 25
    ax.scatter(
        wksp_map_points["longitude"],
        wksp_map_points["latitude"],
        s=marker_size,
        c="#eeeeee",
        edgecolors="#c95f0d",
        linewidths=1,
        alpha=0.85,
    )

    if not wksp_map_points.empty:
        max_n_loc = int(wksp_map_points["n_loc"].max())
        size_ticks = [10, 100, 1000, 10000]
        size_ticks = [tick for tick in size_ticks if tick <= max_n_loc]
        if not size_ticks:
            size_ticks = [max_n_loc]

        legend_handles = [
            ax.scatter(
                [],
                [],
                s=(tick ** 0.5) * 25,
                c="#eeeeee",
                edgecolors="#c95f0d",
                linewidths=1,
                alpha=0.85,
            )
            for tick in size_ticks
        ]
        legend = ax.legend(
            legend_handles,
            [str(tick) for tick in size_ticks],
            title="Workshops per location",
            loc="lower left",
            frameon=True,
        )
        legend.get_frame().set_alpha(0.9)

    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 90)
    ax.set_axis_off()
    fig.tight_layout()
    write_figure(fig, outfile)
    plt.close(fig)

    return outfile


def load_workshop_data():
    wksp = pd.read_csv(REDASH_QUERY_125)
    wksp["start_date"] = pd.to_datetime(wksp["start_date"], errors="coerce")
    wksp["end_date"] = pd.to_datetime(wksp["end_date"], errors="coerce")

    tag_pattern = re.compile("|".join(WORKSHOP_TYPES.keys()))
    wksp = wksp[
        (wksp["end_date"].dt.date <= date.today())
        & (wksp["tag_name"].fillna("").str.contains(tag_pattern))
    ].copy()

    return wksp


def make_workshop_summary_plots():
    wksp = load_workshop_data()

    print(f"working directory: {os.getcwd()}")
    workshops_through_time(wksp)
    workshops_by_year(wksp)
    workshops_map(wksp)


if __name__ == "__main__":
    make_workshop_summary_plots()
